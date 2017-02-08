#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gotyou.crawler import Crawler, Page, FileCacheScheduler, ConsolePipeline, JsonPipeline
from logging.config import dictConfig
import yaml


def textInXpath(node, xpath):
    targetNodes = node.xpath(xpath + '/text()')
    if len(targetNodes) > 0:
        return targetNodes[0]
    else:
        return ''


def process_pokedex(page: Page):
    if page.tag != 'pokedex':
        return

    pokemonXpath = "//*[@id='mw-content-text']/table/tr/td[2]//a/attribute::href"
    # pokemonXpath = "//*[@id='mw-content-text']/table[1]/tr[1]/td[2]/ul/li[1]/a/attribute::href"
    page.addRequest(page.tree.xpath(pokemonXpath), tag='pokemon', headers=headers)


def process_pokemon(page: Page):
    if page.tag != 'pokemon':
        return

    page.addTargetValue('id', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[2]/td/table/tr[2]/td[2]/b"))
    page.addTargetValue('name', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr[1]/td/div/div[3]"))

    types = []
    typeNode = page.tree.xpath("//*[@id='pokemonform-1']/table/tr[2]/td[2]")
    if typeNode:
        for node in typeNode[0]:
            if node.tag == 'span':
                types.append(node.text)
    page.addTargetValue('types', types)

    ability = {'normal': [], 'hidden': ''}
    normalAbilityNode = page.tree.xpath("//*[@id='pokemonform-1']/table/tr[3]/td[2]")
    normal = []
    if normalAbilityNode:
        for node in normalAbilityNode[0]:
            if node.tag == 'a':
                normal.append(node.text)
    ability['normal'] = normal
    ability['hidden'] = textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[4]/td[2]/a")
    page.addTargetValue('ability', ability)

    page.addTargetValue('category', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[5]/td[2]"))
    page.addTargetValue('height', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[6]/td[2]"))
    page.addTargetValue('weight', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[7]/td[2]"))
    page.addTargetValue('hp', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[9]/td[2]"))
    page.addTargetValue('attack', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[10]/td[2]"))
    page.addTargetValue('defense', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[11]/td[2]"))
    page.addTargetValue('sp_attack', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[12]/td[2]"))
    page.addTargetValue('sp_defense', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[13]/td[2]"))
    page.addTargetValue('speed', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[14]/td[2]"))

    eggGroups = []
    eggNode = page.tree.xpath("//*[@id='pokemonform-1']/table/tr[19]/td[2]")
    if eggNode:
        for node in eggNode[0]:
            if node.tag == 'a':
                eggGroups.append(node.text)
    page.addTargetValue('eggGroups', eggGroups)

    page.addTargetValue('eggStep', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[20]/td[2]"))
    page.addTargetValue('gender', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[21]/td[2]"))
    page.addTargetValue('catch', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[22]/td[2]"))
    page.addTargetValue('happiness', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[23]/td[2]"))
    page.addTargetValue('expto100', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[24]/td[2]"))
    page.addTargetValue('baseStat', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[25]/td[2]"))


def pageProcessor(page: Page):
    process_pokedex(page)
    process_pokemon(page)


with open('logconf.yaml') as f:
    logconfig = yaml.load(f)
    dictConfig(logconfig)

domain = 'http://www.pokemon.name'
path = '/wiki/宝可梦列表'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
    'cookie': 'bdshare_firstime=1486483047635; wikiEditor-0-booklet-wikicode-page=tags; wikiEditor-0-booklet-characters2-page=hiragana; wikiEditor-0-booklet-symbols-page=punc; Hm_lvt_5d5b68f5aaae57bdebbe134a5acde926=1486483047; Hm_lpvt_5d5b68f5aaae57bdebbe134a5acde926=1486535657'
}
(Crawler(pageProcessor, domain=domain)
        .addRequest(path, tag='pokedex', headers=headers)
        .setScheduler(FileCacheScheduler('./'))
        .addPipeline(ConsolePipeline())
        .addPipeline(JsonPipeline('./jsons/'))
        .run())
