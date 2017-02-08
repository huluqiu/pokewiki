#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gotyou.crawler import Crawler, Page, FileCacheScheduler, ConsolePipeline, JsonPipeline

domain = 'https://wiki.52poke.com/'
path = 'wiki/宝可梦列表（按全国图鉴编号）/简单版'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'
}


def textInXpath(node, xpath):
    targetNodes = node.xpath(xpath + '/text()')
    if len(targetNodes) > 0:
        return targetNodes[0]
    else:
        return ''


def pageProcessor(page: Page):
    if page.tag == 'detail':
        page.addTargetValue('id', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr/th/a"))
        page.addTargetValue('name', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr/td[1]/span/b"))
        page.addTargetValue('name_jap', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr/td[1]/b[1]/span"))
        page.addTargetValue('name_en', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr/td[1]/b[2]"))
        page.addTargetValue('category', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[3]/td[2]/table/tr/td/table/tr/td"))

        types = []
        typesNode = page.tree.xpath("//*[@id='mw-content-text']/table[2]/tr[3]/td[1]/table/tr/td/table/tr/td")
        if typesNode:
            for node in typesNode[0]:
                types.append(node[0].attrib['title'])
        page.addTargetValue('types', types)

        abilityies = {'normal': [], 'hidden': ''}
        abilityNode = page.tree.xpath("//*[@id='mw-content-text']/table[2]/tr[4]/td/table/tr/td/table/tr/td[1]")
        if abilityNode:
            normals = []
            for node in abilityNode[0]:
                if node.tag == 'a':
                    normals.append(node.text)
            abilityies['normal'] = normals
        abilityies['hidden'] = textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[4]/td/table/tr/td/table/tr/td[2]/a")
        page.addTargetValue('ability', abilityies)
        page.addTargetValue('expto100', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[5]/td/table/tr/td/table/tr/td"))
        page.addTargetValue('height', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[8]/td[1]/table/tr/td/table/tr/td"))
    else:
        pokemonXpath = "//div[@id='mw-content-text']/table[1]/tr[4]/td[2]/a/attribute::href"
        page.addTargetValue('pokemon', page.tree.xpath(pokemonXpath))
        page.addRequest(page.tree.xpath(pokemonXpath), tag='detail', headers=headers)


(Crawler(pageProcessor, domain=domain)
        .addRequest(path, headers=headers)
        .setScheduler(FileCacheScheduler('./crawler/'))
        .addPipeline(ConsolePipeline())
        .addPipeline(JsonPipeline('./crawler/jsons/'))
        .run())
