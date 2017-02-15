#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gotyou.crawler import Crawler, Page, FileCacheScheduler, ConsolePipeline, Pipeline, JsonPipeline
from logging.config import dictConfig
import yaml
import psycopg2
import os

with open('logconf.yaml') as f:
    logconfig = yaml.load(f)
    dictConfig(logconfig)


def textInXpath(node, xpath):
    targetNodes = node.xpath(xpath + '/text()')
    if len(targetNodes) > 0:
        return targetNodes[0]
    else:
        return ''


def process_pokedex(page: Page):
    if page.tag != 'pokedex':
        return

    pokemons = []
    mw_content_text_node = page.tree.xpath("//*[@id='mw-content-text']")[0]
    tables = mw_content_text_node.xpath("table[position()<last()]")
    for gen, table in enumerate(tables):
        for tr in table:
            pokemon_class = tr.xpath("td[1]/b/text()")[0]
            pokemon_ul = tr.xpath("td[2]/ul")[0]
            for li in pokemon_ul:
                num = li.text
                name = li.xpath(".//a/text()")[0]
                pokemons.append((num, name, pokemon_class, gen + 1))
    page.addTargetValue('pokemons', pokemons)

    page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table/tr/td[2]//a/attribute::href"), tag='pokemon')
    # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr[1]/td[2]/ul/li[6]//a/attribute::href"), tag='pokemon')
    # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr[3]/td[2]/ul/li[1]//a/attribute::href"), tag='pokemon')
    # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr[3]/td[2]/ul/li[4]//a/attribute::href"), tag='pokemon')
    # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr[2]/td[2]/ul/li[124]//a/attribute::href"), tag='pokemon')


def process_pokemon(page: Page):
    if page.tag != 'pokemon':
        return

    page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr/td[4]/a/attribute::href"), tag='pokemon_move_map', headers=headers)

    page.addTargetValue('num', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[2]/td/table/tr[2]/td[2]/b"))
    page.addTargetValue('name', textInXpath(page.tree, "//*[@id='mw-content-text']/table[2]/tr[1]/td/table/tr[1]/td/div/div[3]"))
    page.addTargetValue('name_jp_en', textInXpath(page.tree, "//*[@id='mw-content-text']/p"))
    page.addTargetValue('category', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[5]/td[2]"))
    page.addTargetValue('eggStep', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[20]/td[2]"))
    page.addTargetValue('gender', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[21]/td[2]"))
    page.addTargetValue('catch', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[22]/td[2]"))
    page.addTargetValue('happiness', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[23]/td[2]"))
    page.addTargetValue('expto100', textInXpath(page.tree, "//*[@id='pokemonform-1']/table/tr[24]/td[2]"))
    eggGroups = []
    eggNode = page.tree.xpath("//*[@id='pokemonform-1']/table/tr[19]/td[2]")
    if eggNode:
        for node in eggNode[0]:
            if node.tag == 'a':
                eggGroups.append(node.text)
    page.addTargetValue('eggGroups', eggGroups)

    forms = []
    form_names = page.tree.xpath("//*[@id='pokemonforms']/table/tr/td[1]//div/text()")
    tables = page.tree.xpath("//*[@id='pokemonforms']/table/tr/td[2]/div/table")
    for i, table in enumerate(tables):
        types = []
        typeNode = table.xpath("tr[2]/td[2]")
        if typeNode:
            for node in typeNode[0]:
                if node.tag == 'span':
                    types.append(node.text)

        ability = {'normal': [], 'hidden': ''}
        normalAbilityNode = table.xpath("tr[3]/td[2]")
        normal = []
        if normalAbilityNode:
            for node in normalAbilityNode[0]:
                if node.tag == 'a':
                    normal.append(node.text)
        ability['normal'] = normal
        ability['hidden'] = textInXpath(table, "tr[4]/td[2]/a")

        height = textInXpath(table, "tr[6]/td[2]")
        weight = textInXpath(table, "tr[7]/td[2]")
        hp = textInXpath(table, "tr[9]/td[2]")
        attack = textInXpath(table, "tr[10]/td[2]")
        defense = textInXpath(table, "tr[11]/td[2]")
        sp_attack = textInXpath(table, "tr[12]/td[2]")
        sp_defense = textInXpath(table, "tr[13]/td[2]")
        speed = textInXpath(table, "tr[14]/td[2]")
        baseStat = textInXpath(table, "tr[25]/td[2]")

        forms.append((form_names[i], types, ability, height, weight, baseStat, (hp, attack, defense, sp_attack, sp_defense, speed)))
    page.addTargetValue('forms', forms)

    pokemon_evolution = ()
    mw_content_text_node = page.tree.xpath("//*[@id='mw-content-text']")[0]
    evolution_table_index = -1
    for i, child in enumerate(mw_content_text_node):
        if child.tag == 'h3' and child.xpath('string(.)') == '进化':
            evolution_table_index = i + 1
    evolution_table = mw_content_text_node[evolution_table_index].xpath("tr/td/table")[0]
    poke_init_name = evolution_table.xpath("tr/td[1]")[0].xpath('string(.)')
    td2 = evolution_table.xpath("tr/td[2]")
    if len(td2) == 0:
        evolutions = []
    else:
        evolutions = get_evolution(td2[0][0])
    pokemon_evolution = (poke_init_name, evolutions)
    page.addTargetValue('pokemon_evolution', pokemon_evolution)


def get_evolution(table):
    evolutions = []
    for tr in table:
        tds = tr.xpath("td")
        way = tds[0][1].xpath('string(.)')
        condition = tds[0][2].xpath('string(.)')
        evolution_name = tds[1].xpath('string(.)')
        next_evolution_table = tr.xpath('td[3]/table')
        next_evolutions = []
        if len(next_evolution_table) > 0:
            next_evolutions = get_evolution(next_evolution_table[0])
        evolutions.append((way, condition, evolution_name, next_evolutions))
    return evolutions


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
    page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table//a/attribute::href"), tag='ability')
    # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[1]/tr[3]//a/attribute::href"), tag='ability')


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


def process_move_list(page: Page):
    if page.tag == 'move_list':
        # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/div[1]/ul/li[1]//a/attribute::href"), tag='move_type_list')
        page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/div[1]/ul/li//a/attribute::href"), tag='move_type_list')
    elif page.tag == 'move_type_list':
        # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[2]/tr[2]/td[1]/a/attribute::href"), tag='move')
        # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[2]/tr[10]/td[1]/a/attribute::href"), tag='move')
        # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[4]/tr[38]/td[1]/a/attribute::href"), tag='move')
        # page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[4]/tr[49]/td[1]/a/attribute::href"), tag='move')
        page.addRequest(page.tree.xpath("//*[@id='mw-content-text']/table[position()>1]/tr/td[1]//a/attribute::href"), tag='move')


def process_move(page: Page):
    if page.tag != 'move':
        return

    page.addTargetValue('name', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[1]/td/table/tr[1]/td/div[1]"))
    page.addTargetValue('name_jp_en', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[1]/td/table/tr[1]/td/div[2]"))
    page.addTargetValue('description', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[1]/td/table/tr[2]/td"))
    page.addTargetValue('type', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[2]/td/table/tr[2]/td[2]/span"))
    page.addTargetValue('kind', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[2]/td/table/tr[3]/td[2]/span"))
    page.addTargetValue('power', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[2]/td/table/tr[4]/td[2]"))
    page.addTargetValue('accuracy', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[2]/td/table/tr[5]/td[2]"))
    page.addTargetValue('pp', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[2]/td/table/tr[6]/td[2]/b"))
    page.addTargetValue('priority', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[2]/td/table/tr[7]/td[2]"))
    page.addTargetValue('gen', textInXpath(page.tree, "//*[@id='mw-content-text']/p/a[3]"))
    page.addTargetValue('z_stone', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[5]/td/table/tr[2]/td[2]"))
    page.addTargetValue('z_move', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[5]/td/table/tr[3]/td[2]/a"))
    page.addTargetValue('z_power', textInXpath(page.tree, "//*[@id='mw-content-text']/table[1]/tr[5]/td/table/tr[4]/td[2]"))

    mw_content_text_node = page.tree.xpath("//*[@id='mw-content-text']")[0]
    effect_battle = -1
    effect_map = -1
    end = -1
    for i, child in enumerate(mw_content_text_node):
        if child.tag == 'h2' and child.xpath('string(.)') == '战斗效果':
            effect_battle = i
        elif child.tag == 'h2' and child.xpath('string(.)') == '冒险效果':
            effect_map = i
        elif child.tag == 'h2' and child.xpath('string(.)') == '可学会的宝可梦':
            end = i
    page.addTargetValue('effect_battle', mw_content_text_node[effect_battle + 1].xpath('string(.)'))
    if effect_map == -1:
        effect_battle_end = end - 1
    else:
        effect_battle_end = effect_map - 1

    if effect_map == -1:
        page.addTargetValue('effect_map', '')
    else:
        page.addTargetValue('effect_map', mw_content_text_node[effect_map + 1].xpath('string(.)'))

    states = {}
    if effect_battle_end - effect_battle > 1:
        state_nodes = mw_content_text_node[effect_battle + 2:effect_battle_end + 1]
        titles = list(filter(lambda n: n.tag == 'h3', state_nodes))
        dess = list(filter(lambda n: n.tag == 'dl', state_nodes))
        for i, title in enumerate(titles):
            states[title.xpath('string(.)')] = dess[i].xpath('string(.)')
    page.addTargetValue('states', states)


def process_pokemon_move_map(page: Page):
    if page.tag != 'pokemon_move_map':
        return

    page.addTargetValue('num', os.path.basename(page.url))
    pokemon_move_map = []
    mw_content_text_node = page.tree.xpath("//*[@id='mw-content-text']")[0]
    start = -1
    end = -1
    for i, node in enumerate(mw_content_text_node):
        if node.tag == 'h2' and node.xpath('string(.)') == '招式':
            start = i + 1
        if node.tag == 'h2' and node.xpath('string(.)') == '相关链接':
            end = i
    nodes = mw_content_text_node[start:end]
    h3s = list(filter(lambda n: n.tag == 'h3', nodes))
    tables = list(filter(lambda n: n.tag == 'table', nodes))
    for i, h3 in enumerate(h3s):
        table = tables[i]
        way = h3.xpath('string(.)')
        moves = []
        for tr in table[1:]:
            condition = tr[0].xpath('string(.)')
            move_name = tr[2].xpath('string(.)')
            form = tr[8].xpath('string(.)')
            moves.append((condition, move_name, form))
        pokemon_move_map.append((way, moves))
    page.addTargetValue('pokemon_move_map', pokemon_move_map)


def pageProcessor(page: Page):
    process_pokedex(page)
    process_pokemon(page)
    process_pokemon_move_map(page)
    process_ability_list(page)
    process_ability(page)
    process_move_list(page)
    process_move(page)


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


domain = 'http://www.pokemon.name'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
    'cookie': 'bdshare_firstime=1486483047635; wikiEditor-0-booklet-wikicode-page=tags; wikiEditor-0-booklet-characters2-page=hiragana; wikiEditor-0-booklet-symbols-page=punc; Hm_lvt_5d5b68f5aaae57bdebbe134a5acde926=1486483047; Hm_lpvt_5d5b68f5aaae57bdebbe134a5acde926=1486901302'
}
(Crawler(pageProcessor, domain=domain, headers=headers)
        .addRequest('/wiki/特性/按世代分类', tag='ability_list')
        .addRequest('/wiki/宝可梦列表', tag='pokedex')
        .addRequest('/wiki/招式列表', tag='move_list')
        .setScheduler(FileCacheScheduler('.'))
        .addPipeline(ConsolePipeline())
        .addPipeline(JsonPipeline('jsons'))
        .run())
