#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gotyou.crawler import Crawler, ConsolePipeline

domain = 'https://wiki.52poke.com/'
path = 'wiki/宝可梦列表（按全国图鉴编号）/简单版'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'
}


def pageProcessor(page):
    if page.tag is 'detail':
        namePath = "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr/td[1]/span/b/text()"
        page.addTargetValue('name', page.tree.xpath(namePath))
    else:
        pokemonXpath = "//div[@id='mw-content-text']/table[1]/tr[4]/td[2]/a/attribute::href"
        page.addTargetValue('pokemon', page.tree.xpath(pokemonXpath))
        page.addRequest(page.tree.xpath(pokemonXpath), tag='detail', headers=headers)


(Crawler(pageProcessor, domain=domain)
        .addRequest(path, headers=headers)
        .addPipeline(ConsolePipeline)
        .run())
