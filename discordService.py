# coding:UTF-8

from ImageSearchService import ImageSearchService
from dataBaseService import DataBaseService
import random
from datetime import datetime, timedelta,  timezone
import os


class DiscordService():

    # コンストラクタ
    def __init__(self, client):
        # Discordのcクライアントを設定する
        self.client = client
        # ボットのIDを取得する
        self.botId = os.environ.get('ID_BOT')
        # ボットのIDを整形する
        self.botId = self.botId.strip("<").strip("@").strip("!").strip(">")
        # タイムゾーンの設定する
        self.timeZone = timezone(timedelta(hours=+9), 'JST')
        # データベースサービスのインスタンスを生成する
        self.dataBaseService = DataBaseService()

    # メッセージ受信時に動作する処理
    async def on_message(self, message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        # BOTに対するメンションでなかった場合は無視する
        if self.botId not in message.content:
            return
        # 先頭の文字が検索だった場合、キーワードで画像検索を行い、返却する
        if '!検索' == message.content.split()[1]:
            searchWard = ''
            for index, string in enumerate(message.content.split()):
                # 0,1番目はスキップする
                if index == 0 or index == 1:
                    continue
                # 3番目以降の場合、+を連結する
                if index >= 3:
                    searchWard += '+'
                # 文字列を連結する
                searchWard += string
            link = ImageSearchService().searchImage(searchWard)

            # メッセージを送信する
            await message.channel.send('「' + searchWard + '」の画像です')

            # 画像を送信する
            await message.channel.send(link)
            return

        # メッセージに対して返事をする
        await self.replyMessage(message)

    # 1分毎に実行される処理
    async def executeForOneMinute(self):
        # 現在の時刻を取得する
        now = datetime.now(self.timeZone)
        nowDate = now.strftime('%Y/%m/%d')
        nowTime = now.strftime('%H:%M')
        nowWeek = now.strftime('%a')

        # 10分単位で処理を行う
        if nowTime[4] == '0':
            # データベースに接続する
            connection = self.dataBaseService.connectionDataBase()
            # リマインド情報を取得する
            remindInfoList = self.dataBaseService.selectRemind(
                connection, nowTime, nowWeek, nowDate)
            # データベースから切断する
            self.dataBaseService.disconnectDataBase(connection)
            # メッセージを送信する
            await self.sendRemind(remindInfoList)

        # 23時に実行される処理
        if nowTime == '23:00':
            # データベースに接続する
            connection = self.dataBaseService.connectionDataBase()
            # DBから画像検索用のキーワードを取得する
            keyward = self.dataBaseService.selectImageSearchKeyward(connection)
            # データベースから切断する
            self.dataBaseService.disconnectDataBase(connection)
            # 画像検索を行う
            link = ImageSearchService().searchImage(keyward[0][0])
            # チャンネルを設定
            channel = self.client.get_channel(
                int(os.environ.get('CHANNEL_DISCORD')))
            # メッセージを送信する
            await channel.send(link)

            # discordにリマインドを送信する
    async def sendRemind(self, remindInfoList):
        # メッセージが取得できなかった場合は処理を行わない
        if len(remindInfoList) == 0:
            return

        # メッセージを出力する
        for remindInfo in remindInfoList:
            message = remindInfo[4]
            sendTarget = remindInfo[5]
            sendChannel = remindInfo[6]

            # チャンネルを設定
            channel = self.client.get_channel(int(os.environ.get(sendChannel)))

            # メッセージを設定
            sendMsg = ''
            if sendTarget is not None:
                sendMsg += os.environ.get(sendTarget) + ' '
            sendMsg += message

            # メッセージを送信
            await channel.send(sendMsg)

    # メッセージに対して返事をする
    async def replyMessage(self, message):
        # DBに接続する
        connection = self.dataBaseService.connectionDataBase()

        # Botのトリガー情報のリストを取得する
        triggerInfoList = self.dataBaseService.selectTrigger(connection)

        messageList = None
        for triggerInfo in triggerInfoList:

            trigger = triggerInfo[0]
            messageId = str(triggerInfo[1])

            # メッセージにトリガーが含まれていた場合
            if trigger in message.content:
                # トリガーに対応するメッセージを取得する
                messageList = self.dataBaseService.selectMessageByID(
                    connection, messageId)
                break

        # メッセージにトリガーが含まれていなかった場合
        if messageList is None:
            # 汎用メッセージを取得する
            messageList = self.dataBaseService.selectMessageByID(
                connection, "0")

        # データベースから切断する
        self.dataBaseService.disconnectDataBase(connection)
        # メッセージをランダムに選択する
        countMessage = len(messageList)
        randomNumber = int(random.random() * countMessage)
        # メッセージを送信する
        await message.channel.send(messageList[randomNumber][0])
