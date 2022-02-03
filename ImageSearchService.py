# coding:UTF-8

import os

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

    def searchImage(self, data):

        page_limit = 1
        start_index = 1
        response = []
        for page in range(0, page_limit):
            try:
                response.append(self.service.cse().list(
                    q=data,
                    cx=self.customSearchEngineId,
                    lr='lang_ja',
                    num=1,
                    start=start_index,
                    searchType='image'
                ).execute())
                start_index = response[page].get("queries").get("nextPage")[
                    0].get("startIndex")
            except Exception as e:
                print(e)
                break

        imagePath = response[0]['items'][0]['link']
        print(imagePath)

        return imagePath
