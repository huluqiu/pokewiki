import os
import gotyou
import re
from pathlib import PurePath

_jsonpath = os.path.join(PurePath(os.path.realpath(__file__)).parent, 'jsons')

_error_name_map = {
    '可拉可拉': '卡拉卡拉',
    '呆河马': '呆壳兽',
    '河马王': '呆呆王',
    '雷电球': '霹雳电球',
    '嘎拉嘎拉': '嘎啦嘎啦',
    '巴尔郎': '无畏小子',
    '柯波郎': '战舞郎',
    '绵绵': '茸茸羊',
    '牛蛙君': '蚊香蛙皇',
    '爱哭鬼': '盆才怪',
    '爱哭树': '盆才怪',
    '阳阳玛': '蜻蜻蜓',
    '3D龙': '多边兽',
    '3D龙2': '多边兽Ⅱ',
    '3D龙Z': '多边兽Ｚ',
    '艾比郎': '快拳郎',
    '沙瓦郎': '飞腿郎',
    '由基拉': '幼基拉斯',
    '沙基拉': '沙基拉斯',
    '班吉拉': '班基拉斯',
    '梅卡阳玛': '远古巨蜓',
    '沙漠奈亚': '刺球仙人掌',
    '梦歌奈亚': '梦歌仙人掌',
    '夜巨人': '彷徨夜灵',
    '夜黑魔人': '黑夜魔灵',
    '暴蝾螈': '暴飞龙',
    '泳气鼬': '泳圈鼬',
    '附和气球': '随风球',
    '吸盘魔偶': '魔墙人偶',
    '怪河马': '沙河马',
    '紫天蝎': '钳尾蝎',
    '波波鸽': '咕咕鸽',
    '轰隆雉鸡': '高傲雉鸡',
    '修缮老头': '修建老匠',
    '首席天鹅': '舞天鹅',
    '芽吹鹿': '萌芽鹿',
    '暴露菇': '败露球菇',
    '宝贝球菇': '哎呀球菇',
    '秃鹰小子': '秃鹰丫头',
    '攉土兔': '掘掘兔',
    '烈箭鹟': '烈箭鹰',
    '咩咩羊': '坐骑小羊',
    '电伞查特': '光电伞蜥',
}

_move_error_name_map = {
    '硝化冲锋': '蓄能焰袭',
    '酸液炸弹': '酸液爆弹',
}

_pokemon_num_name_map = {}
_pokemon_name_num_map = {}
_ability_num_name_map = {}
_ability_name_num_map = {}
_move_num_name_map = {}
_move_name_num_map = {}

_pokemons = []
_pokemon_forms = []
_pokemon_evolutions = []
_abilities = []
_pokemon_ability_map = []
_pokemon_move_map = []


def _init_map():
    pokedex = gotyou.jsonload(os.path.join(_jsonpath, 'pokedex/_wiki_宝可梦列表.json'))['pokemons']
    for (num, name, pokemon_class, gen) in pokedex:
        num = int(num.replace(' ', '').replace('.', ''))
        name = name.replace('\u200e', '')
        _pokemon_num_name_map[num] = (num, name, pokemon_class, gen)
        _pokemon_name_num_map[name] = num

    ability_list = gotyou.jsonload(os.path.join(_jsonpath, 'ability_list_52/_wiki_特性列表.json'))['abilities']
    for (num, name, gen) in ability_list:
        re_v = re.compile(r'(.+)\n')
        num = int(re_v.match(num).group(1))
        name = re_v.match(name).group(1)
        _ability_name_num_map[name] = (num, name, gen)
        _ability_num_name_map[num] = name

    move_list = gotyou.jsonload(os.path.join(_jsonpath, 'move_list_52/_wiki_招式列表.json'))['move_list']
    pre_name = ''
    index = 1
    for (num, name, name_jp, name_en, gen) in move_list:
        re_v = re.compile(r' (.+)\n')
        num = int(re_v.match(num).group(1))
        name = re_v.match(name).group(1)
        name_jp = re_v.match(name_jp).group(1)
        name_en = re_v.match(name_en).group(1)
        if gen == 7:
            gen = 6
        elif gen == 8:
            gen = 7
        if name == pre_name:
            continue
        else:
            pre_name = name
            _move_name_num_map[name] = (index, name, name_jp, name_en, gen)
            _move_num_name_map[index] = name
            index += 1


_init_map()


def _formmater(s):
    s = s.replace('\n', '').replace(' ', '')
    return s


def _solvepokemons():
    def add_evolution(l, init_name, evolutions):
        if init_name and evolutions:
            init_name = init_name.replace('\u200e', '')
            if init_name in _error_name_map:
                init_name = _error_name_map[init_name]
            for (way, condition, evolution_name, next_evolutions) in evolutions:
                evolution_name = evolution_name.replace('\u200e', '')
                if evolution_name in _error_name_map:
                    evolution_name = _error_name_map[evolution_name]
                if way != '超进化':
                    l.append((_pokemon_name_num_map[init_name], _pokemon_name_num_map[evolution_name], way, condition))
                add_evolution(l, evolution_name, next_evolutions)

    path = os.path.join(_jsonpath, 'pokemon')
    pokemon_objs = list(gotyou.jsonload(os.path.join(path, filename)) for filename in os.listdir(path))
    pokemon_objs = sorted(pokemon_objs, key=lambda obj: obj['num'])
    for pokemon in pokemon_objs:
        num, name, pokemon_class, gen = _pokemon_num_name_map[int(pokemon['num'])]
        name = pokemon['name']
        m = re.match(r'（(.+)、(.+)）是', pokemon['name_jp_en'])
        name_jp = m.group(1)
        name_en = m.group(2)
        category = pokemon['category']
        m = re.findall(r'\d+', pokemon['eggStep'])
        eggStep = m[1]
        m = re.findall(r'\d+', pokemon['gender'])
        if m:
            t = list(map(lambda n: int(n), m))
            male_rate = t[0] / (t[0] + t[1])
            female_rate = t[1] / (t[0] + t[1])
        else:
            male_rate = 0
            female_rate = 0
        catch = int(pokemon['catch'])
        happiness = int(pokemon['happiness'])
        expto100 = int(pokemon['expto100'].replace(',', ''))
        egg_groups = pokemon['eggGroups']
        _pokemons.append((num, name, name_jp, name_en, pokemon_class, category,
                        egg_groups, eggStep, male_rate, female_rate, catch,
                        happiness, expto100, gen))

        for i, form in enumerate(pokemon['forms']):
            form_name, types, abilit_dic, height, weight, stats_get, stats = form
            types = list(filter(lambda n: n, types))
            height = float(height.split('m')[0])
            weight = float(weight.split('kg')[0])
            stats = tuple(int(v) for v in stats)
            stats_map = {'HP': 0, '攻击': 0, '防御': 0, '特攻': 0, '特防': 0, '速度': 0}
            stats_get = stats_get.split('、')
            for v in stats_get:
                v = v.split('+')
                stats_map[v[0]] = int(v[1])
            stats_get = tuple(v for k, v in stats_map.items())
            if i == 0:
                is_normal = True
            else:
                is_normal = False
            _pokemon_forms.append((num, form_name, types, height, weight, stats, stats_get, is_normal))

            for normal_ability in abilit_dic['normal']:
                _pokemon_ability_map.append((num, _ability_name_num_map[normal_ability][0], form_name, False))
            if abilit_dic['hidden'] and abilit_dic['hidden'] not in abilit_dic['normal']:
                _pokemon_ability_map.append((num, _ability_name_num_map[abilit_dic['hidden']][0], form_name, True))

        init_name, evolutions = pokemon['pokemon_evolution']
        add_evolution(_pokemon_evolutions, init_name, evolutions)


def get_gens():
    return [gen for gen in range(1, 8)]


def get_pokemon_class():
    return set(v[2] for i, v in _pokemon_num_name_map.items())


def get_egg_groups():
    egg_groups = gotyou.jsonload(os.path.join(_jsonpath, 'egg_groups/_wiki_生蛋分组.json'))['egg_groups']
    return [e for e in map(lambda n: tuple(map(_formmater, n)), egg_groups)]


def get_types():
    return gotyou.jsonload(os.path.join(_jsonpath, 'types/_wiki_属性.json'))['types']


def get_kinds():
    return ['物理', '特殊', '变化', 'z']


def get_pokemons():
    if not _pokemons:
        _solvepokemons()
    return _pokemons


def get_forms():
    if not _pokemon_forms:
        _solvepokemons()
    return _pokemon_forms


def get_evolutions():
    if not _pokemon_evolutions:
        _solvepokemons()
    return set(_pokemon_evolutions)


def get_abilities():
    abilities = []
    ability_list_dic = gotyou.jsonload(os.path.join(_jsonpath, 'ability_list/_wiki_特性_按世代分类.json'))
    for (k, v) in ability_list_dic.items():
        for i, name in enumerate(v['name']):
            if name in _ability_name_num_map:
                num = _ability_name_num_map[name][0]
                gen = _ability_name_num_map[name][2]
                name_jp = v['name_jp'][i]
                name_en = v['name_en'][i]
                effect = v['effect'][i].replace('\n', '')
                _ability_name_num_map[name] = (num, name, name_jp, name_en, gen, effect)
    path = os.path.join(_jsonpath, 'ability')
    ability_objs = list(gotyou.jsonload(os.path.join(path, filename)) for filename in os.listdir(path))
    for ability in ability_objs:
        if ability['name'] in _ability_name_num_map:
            num, name, name_jp, name_en, gen, effect = _ability_name_num_map[ability['name']]
            abilities.append((num, name, name_jp, name_en, effect, ability['effect_battle'], ability['effect_map'], gen))
    abilities = sorted(abilities, key=lambda n: n[0])
    return abilities


def get_pokemon_ability_map():
    if not _pokemon_ability_map:
        _solvepokemons()
    return _pokemon_ability_map


def get_moves():
    moves = []
    path = os.path.join(_jsonpath, 'move')
    move_objs = list(gotyou.jsonload(os.path.join(path, filename)) for filename in os.listdir(path))
    for move in move_objs:
        if move['name'] in _move_error_name_map:
            move['name'] = _move_error_name_map[move['name']]
        num, name, name_jp, name_en, gen = _move_name_num_map[move['name']]
        kind = move['kind']
        if kind == '':
            kind = 'z'
        power = move['power'].replace('\n', '').replace('--', '')
        if power == '变动':
            power = 0
        elif power:
            power = int(power)
        else:
            power = -1
        accuracy = move['accuracy'].replace('\n', '').replace('--', '')
        if accuracy:
            accuracy = int(accuracy)
        else:
            accuracy = -1
        pp = move['pp']
        if pp:
            pp = int(pp)
        else:
            pp = 1
        priority = move['priority'].replace('\n', '')
        if priority:
            try:
                priority = int(priority)
            except ValueError:
                priority = 0
        else:
            priority = 0
        z_stone = move['z_stone'].replace('\n', '')
        z_move = move['z_move'].replace('\n', '')
        z_power = move['z_power'].replace('\n', '')
        moves.append((num, name, name_jp, name_en, move['type'], kind, power, accuracy, pp, move['description'], move['effect_battle'], move['effect_map'], priority, gen, z_stone, z_move, z_power))
    moves = sorted(moves, key=lambda n: n[0])
    return moves


def get_pokemon_move_map():
    pokemon_move_map = []
    path = os.path.join(_jsonpath, 'pokemon_move_map')
    map_objs = list(gotyou.jsonload(os.path.join(path, filename)) for filename in os.listdir(path))
    for obj in map_objs:
        poke_num = int(obj['num'])
        for maps in obj['pokemon_move_map']:
            way, m = maps
            for move_info in m:
                condition, name, form = move_info
                if name in _move_error_name_map:
                    name = _move_error_name_map[name]
                move_num = _move_name_num_map[name][0]
                pokemon_move_map.append((poke_num, move_num, way, condition, form))
    pokemon_move_map = sorted(pokemon_move_map, key=lambda n: n[0])
    return pokemon_move_map


if __name__ == "__main__":
    print(get_pokemon_class())
    print(get_egg_groups())
    print(get_types())
    print(len(get_pokemons()))
    print(len(get_evolutions()))
    print(len(get_abilities()))
    print(len(get_moves()))
    print(len(get_pokemon_move_map()))
    print(len(get_pokemon_ability_map()))
    print(len(get_forms()))
