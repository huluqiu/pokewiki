#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gotyou.crawler import Crawler, Page, FileCacheScheduler, ConsolePipeline, Pipeline
from logging.config import dictConfig
import yaml
import psycopg2

with open('logconf.yaml') as f:
    logconfig = yaml.load(f)
    dictConfig(logconfig)

domain = 'http://www.pokemon.name'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
    'cookie': 'bdshare_firstime=1486483047635; wikiEditor-0-booklet-wikicode-page=tags; wikiEditor-0-booklet-characters2-page=hiragana; wikiEditor-0-booklet-symbols-page=punc; Hm_lvt_5d5b68f5aaae57bdebbe134a5acde926=1486483047; Hm_lpvt_5d5b68f5aaae57bdebbe134a5acde926=1486901302'
}


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
    # pokemonXpath = "//*[@id='mw-content-text']/table[1]/tr[1]/td[2]/ul/li[3]//a/attribute::href"
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


def process_ability_list(page: Page):
    if page.tag != 'ability_list':
        return

    genNodes = page.tree.xpath("//*[@id='mw-content-text']/h3")
    abilityTables = page.tree.xpath("//*[@id='mw-content-text']/table")
    for i, gen in enumerate(genNodes):
        table = abilityTables[i]
        v = {}
        v['gen'] = gen.xpath("span/text()")
        v['name'] = table.xpath("tr/td[1]/a/text()")
        v['name_jp'] = table.xpath("tr/td[2]/text()")
        v['name_en'] = table.xpath("tr/td[3]/text()")
        v['effect'] = table.xpath("tr/td[4]/text()")
        page.addTargetValue(str(i), v)
    page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table//a/attribute::href", tag='ability', headers=headers))
    # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr[3]//a/attribute::href"), tag='ability', headers=headers)


def process_ability(page: Page):
    if page.tag != 'ability':
        return

    page.addTargetValue('name', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr/td/table/tr[1]/td/div[1]"))
    effect_battle = -1
    effect_map = -1
    end = -1
    mw_content_text_node = page.tree.xpath("//*[@id='mw-content-text']")[0]
    for i, child in enumerate(mw_content_text_node):
        if child.tag == 'h2' and child.xpath('string(.)') == '战斗效果':
            effect_battle = i
        elif child.tag == 'h2' and child.xpath('string(.)') == '地图效果':
            effect_map = i
        elif child.tag == 'h2' and child.xpath('string(.)') == '持有该特性的宝可梦':
            end = i
    if effect_map == -1:
        effect_battle = mw_content_text_node[end - 1].xpath('string(.)')
    else:
        effect_battle = mw_content_text_node[effect_map - 1].xpath('string(.)')
    page.addTargetValue('effect_battle', effect_battle)
    if effect_map == -1:
        page.addTargetValue('effect_map', '')
    else:
        page.addTargetValue('effect_map', mw_content_text_node[end - 1].xpath('string(.)'))


def pageProcessor(page: Page):
    # process_pokedex(page)
    # process_pokemon(page)
    process_ability_list(page)
    process_ability(page)


class PsycopgPipeline(Pipeline):

    """Docstring for PsycopgPipeline. """

    def __init__(self, dbname):
        Pipeline.__init__(self)

        self.con = psycopg2.connect(dbname=dbname)
        self.cursor = self.con.cursor()

    def __del__(self):
        if self.con.get_transaction_status() != psycopg2.extensions.TRANSACTION_STATUS_IDLE:
            self.con.commit()

        self.cursor.close()
        self.con.close()

    def process(self, page: Page):
        if self.con.get_transaction_status() != psycopg2.extensions.TRANSACTION_STATUS_IDLE:
            self.con.commit()


(Crawler(pageProcessor, domain=domain)
        # .addRequest('/wiki/特性/按世代分类', tag='ability_list', headers=headers)
        .addRequest('/wiki/宝可梦列表', tag='pokedex', headers=headers)
        .setScheduler(FileCacheScheduler('.'))
        .addPipeline(ConsolePipeline())
        # .addPipeline('jsons')
        .run())
