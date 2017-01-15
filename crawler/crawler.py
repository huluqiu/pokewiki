#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from lxml import etree

domain = 'https://wiki.52poke.com/'
path = 'wiki/宝可梦列表（按全国图鉴编号）/简单版'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'
}
response = requests.get(domain + path, headers=headers)
root = etree.HTML(response.text)
table = root.xpath("//div[@id='mw-content-text']/table[1]")[0]
for child in table[2:]:
    if len(child) == 1:
        gen = child.xpath(".//span[@class='mw-headline']")[0]
        print(gen.text)
    else:
        pokemon = child.xpath("td[2]/a[1]")[0]
        print(pokemon.text)


class Crawler(object):

    """一个爬虫引擎呀"""

    def __init__(self, pageProcessor):
        """通过pageProcessor初始化

        :pageProcessor: TODO
        :returns: TODO

        """
        self._pageProcessor = pageProcessor

    def addUrl(self, url):
        """添加初始url

        :url: TODO
        :returns: TODO

        """
        self.url = url
        return self

    def setScheduler(self, scheduler):
        """设置scheduler, 用于管理抓取队列

        :scheduler: TODO
        :returns: TODO

        """
        self.scheduler = scheduler
        return self

    def addPipeline(self, pipeline):
        """用于处理抓取到的数据

        :pipeline: TODO
        :returns: TODO

        """
        self.pipeline = pipeline
        return self

    def run(self):
        """启动爬虫
        :returns: TODO

        """
        self.data = self._pageProcessor()
        self.scheduler(self.url)
        self.pipeline(self.data)


def test_pageProcessor():
    data = {'a': 1, 'b': 2, 'c': 3}
    return data


def test_scheduler(url):
    print(url)


def test_pipeline(data):
    for key, value in data.items():
        print(key, value)


Crawler(test_pageProcessor).addUrl(domain).setScheduler(test_scheduler).addPipeline(test_pipeline).run()
