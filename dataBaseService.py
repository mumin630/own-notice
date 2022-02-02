# coding:UTF-8

import psycopg2
import os


class DataBaseService():

    # コンストラクタ
    def __init__(self):
        # DBのURLを取得する
        self.dataBaseURL = os.environ.get('DATABASE_URL')

    # DBに接続する
    def connectionDataBase(self):
        connection = psycopg2.connect(self.dataBaseURL, sslmode='require')
        return connection

    # DBから切断する
    def disconnectDataBase(self, connection):
        connection.close()

    # DBからBotのトリガー情報のリストを取得する
    def selectTrigger(self, connection):

        cursor = connection.cursor()

        sql = "SELECT trigger, messageId FROM reply_trigger "
        sql += "ORDER BY priority"

        cursor.execute(sql)
        triggerInfoList = cursor.fetchall()

        cursor.close()

        return triggerInfoList

    # DBからメッセージIDに紐づくメッセージのリストを取得する
    def selectMessageByID(self, connection, messageId):

        cursor = connection.cursor()

        # メッセージを取得する
        sql = "SELECT message FROM reply_message "
        sql += "WHERE messageId = " + messageId + " "

        cursor.execute(sql)
        messageList = cursor.fetchall()

        cursor.close()

        return messageList

    # DBからリマインドを取得する
    def selectRemind(self, connection, time, week, date):

        cursor = connection.cursor()

        # DBからリマインド情報を取得する
        sql = "SELECT * FROM notice "
        sql += "WHERE "
        sql += "  1 = 1 "
        sql += "  AND time = '" + time + "' "
        sql += "  AND week = '" + week + "' "
        sql += "  AND (date = '" + date + "' "
        sql += "      OR date IS NULL ) "

        cursor.execute(sql)
        remindInfoList = cursor.fetchall()

        cursor.close()

        # リマインド情報のリストを返却する
        return remindInfoList
