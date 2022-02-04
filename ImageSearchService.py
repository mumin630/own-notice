# coding:UTF-8

import os
import random

from googleapiclient.discovery import build


class ImageSearchService():

    # コンストラクタ
    def __init__(self):
        # 環境変数を取得する
        self.googleApiKey = os.environ.get('GOOGLE_API_KEY')
        self.customSearchEngineId = os.environ.get('CUSTOM_SEARCH_ENGINE_ID')

        # Google画像検索のサービスを生成
        self.service = build("customsearch", "v1",
                             developerKey=self.googleApiKey)

    # 画像を検索し、そのURLを返却する
    def searchImage(self, data):

        # ランダムで検索するページを選択する
        startIndex = int(random.random() * 3) * 10 + 1

        # 画像検索を行う
        response = self.service.cse().list(
            q=data,
            cx=self.customSearchEngineId,
            lr='lang_ja',
            num=10,
            start=startIndex,
            searchType='image'
        ).execute()

        # ランダムで画像を選択する
        index = int(random.random() * len(response['items']))
        imagePath = response['items'][index]['link']

        return imagePath
