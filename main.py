# coding:UTF-8

import discord
import os
from discordService import DiscordService
from discord.ext import tasks


# メイン関数
def main():
    # 接続に必要なオブジェクトを生成する
    client = discord.Client()

    # メッセージ受信時に動作する処理
    @client.event
    async def on_message(message):
        # メッセージ受信時に動作する処理を呼び出す
        await discordService.on_message(message)

    # 1分毎に実行される処理
    @tasks.loop(seconds=60)
    async def executeForOneMinute():
        # 待機
        await client.wait_until_ready()
        # 1分毎に実行される処理を呼び出す
        await discordService.executeForOneMinute()

    # Discordサービスのインスタンスを生成する
    discordService = DiscordService(client)
    # トークンを取得する
    token = os.environ.get('TOKEN_DISCORD_OWN_NOTICE')
    # 60秒に一回実行される処理の開始
    executeForOneMinute.start()
    # Botの起動とDiscordサーバーへの接続を行う
    client.run(token)


# 処理を実行する
main()
