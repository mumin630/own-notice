# coding:UTF-8

import requests
import random
import bs4
import ssl
import urllib.parse

ssl._create_default_https_context = ssl._create_unverified_context


class ImageSearchService():

    def searchImage(self, data):

        # 検索対象の文字列をURLエンコードする
        encodeData = urllib.parse.quote(data)
        print(encodeData)

        # Googleで検索する
        response = requests.get("https://www.google.com/search?hl=jp&q=" +
                                encodeData + "&btnG=Google+Search" +
                                "&tbs=0&safe=off&tbm=isch")

        # HTMLからimgタグのsrc要素を抜き出す
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        links = soup.find_all("img")
        link = random.choice(links).get("src")

        # 画像へのリンクを返却する
        print(link)
        return link
