# coding:UTF-8
import discord
import psycopg2
import os
import random
from discord.ext import tasks
from datetime import datetime, timedelta,  timezone

# 環境変数を取得する
TOKEN = os.environ.get('TOKEN_DISCORD_OWN_NOTICE')
ID_BOT = os.environ.get('ID_BOT')
DATABASE_URL = os.environ.get('DATABASE_URL')

# IDの整形
ID_BOT = ID_BOT.strip("<").strip("@").strip("!").strip(">")

# 接続に必要なオブジェクトを生成
client = discord.Client()

# タイムゾーンの設定
JST = timezone(timedelta(hours=+9), 'JST')


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # BOTに対するメンションでなかった場合は無視する
    if ID_BOT not in message.content:
        return

    # DB接続
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    # トリガーを取得する
    sql = "SELECT trigger, messageId FROM reply_trigger "
    sql += "ORDER BY priority"

    cursor.execute(sql)
    rows = cursor.fetchall()

    # メッセージに返信する
    doReply = False
    for row in rows:
        trigger = row[0]
        messageId = str(row[1])

        # メッセージにトリガーが含まれていた場合
        if trigger in message.content:

            # メッセージを取得する
            sql = "SELECT message FROM reply_message "
            sql += "WHERE messageId = " + messageId + " "

            cursor.execute(sql)
            messages = cursor.fetchall()

            # メッセージを選択する
            countMsg = len(messages)
            r_num = int(random.random() * countMsg)

            # メッセージを送信する
            await message.channel.send(messages[r_num][0])

            # 返信フラグを返信済みにする
            doReply = True

    # メッセージにトリガーが含まれていなかった場合
    if doReply is False:

        # メッセージを取得する
        sql = "SELECT message FROM reply_message "
        sql += "WHERE messageId = 0 "

        cursor.execute(sql)
        messages = cursor.fetchall()

        # メッセージを選択する
        countMsg = len(messages)
        r_num = int(random.random() * countMsg)

        # メッセージを送信する
        await message.channel.send(messages[r_num][0])

    # DBクローズ
    cursor.close()
    conn.close()


# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():

    # 待機
    await client.wait_until_ready()

    # 現在の時刻を取得する
    now_date = datetime.now(JST).strftime('%Y/%m/%d')
    now_time = datetime.now(JST).strftime('%H:%M')
    now_week = datetime.now(JST).strftime('%a')
    print(now_date + '(' + now_week + ') ' + now_time)

    # 10分単位で処理を行う
    if now_time[4] != '0':
        return

    # DB接続
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    # メッセージを取得する
    sql = "SELECT * FROM notice "
    sql += "WHERE "
    sql += "  1 = 1 "
    sql += "  AND time = '" + now_time + "' "
    sql += "  AND week = '" + now_week + "' "
    sql += "  AND (date = '" + now_date + "' "
    sql += "      OR date IS NULL ) "

    cursor.execute(sql)
    rows = cursor.fetchall()

    # メッセージが取得できなかった場合は処理を行わない
    if len(rows) == 0:
        return

    # メッセージを出力する
    for row in rows:
        message = row[4]
        sendTarget = row[5]
        sendChannel = row[6]

        # チャンネルを設定
        channel = client.get_channel(int(os.environ.get(sendChannel)))

        # メッセージを設定
        sendMsg = ''
        if sendTarget is not None:
            sendMsg += os.environ.get(sendTarget) + ' '
        sendMsg += message

        # メッセージを送信
        await channel.send(sendMsg)

    # DBクローズ
    cursor.close()
    conn.close()

# ループ処理実行
loop.start()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
