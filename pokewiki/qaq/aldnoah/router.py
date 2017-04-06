import yaml
from django.apps import apps
from enum import Enum
from . import urimanager

# uri: qaq://Pokemon:name
# uri: qaq://Pokemon:name=皮卡丘
# uri: qaq://Move:name/name_en

# cn1 \
# cn2 - >flag - > url
# cn3 /

DOMAIN_WORD_FLAG = 'poke'

Router = apps.get_model('qaq', 'Router')

_sign_map = {}

_attribute_extend_map = {}

_value_filter = set()

_quantifier = set()


class Flag(Enum):
    Entity = 'we'
    EntityIndex = 'wi'
    Attribute = 'wa'
    Value = 'wv'
    AttrValue = 'wav'
    Relation = 'wr'
    Sign = 'ws'
    Paired = 'wp'
    AttributeExtend = 'wae'
    Quantifier = 'wq'
    Any = '*'


class Sign(Enum):
    Equal = '='
    Great = '>'
    Less = '<'
    Contain = '@>'
    GreatTE = '>='
    LessTE = '<='
    In = '<@'
    Not = '!'
    NotEqual = '!='
    NotGreat = '!>'
    NotLess = '!<'
    NotContain = '!@>'
    NotGreatTE = '!>='
    NotLessTE = '!<='
    NotIn = '!<@'


class AttributeExtend(Enum):
    Avg = 'avg'
    Count = 'count'
    Max = 'max'
    Min = 'min'
    Sum = 'sum'
    Species = 'species'


def is_domainword(flag):
    return flag == DOMAIN_WORD_FLAG


def geturi(word):
    """
    从数据库中查询单词对应的 uri 和 flag, 可能多个

    @return: [(uri, flag)]
    """
    queryset = Router.objects.filter(cns__contains=[word])
    return list(queryset.values('uri', 'flag'))


def _getflag(url, t: Flag):
    return t.value


def _flattendict(d):
    r = {}
    for k, v in d.items():
        for e in v:
            r[e] = k
    return r


def register_domainuri(path):
    """根据 yaml 配置, 注册 uri.

    :param path: path of yaml
    """
    def traverse_attr(uri, attribute):
        routers = []
        for k, v in attribute.items():
            a_uri = urimanager.append(uri, path=k)
            flag = _getflag(a_uri, Flag.Attribute)
            if isinstance(v, list):
                # 属性值
                cns = v
            elif isinstance(v, dict):
                # 属性对象
                cns = v.get('cn', [])
                index = v.get('index', None)
                if index:
                    a_uri = urimanager.setindex(a_uri, index)
                    flag = _getflag(a_uri, Flag.Attribute)
                attribute = v.get('attribute', None)
                if attribute:
                    routers.extend(traverse_attr(a_uri, attribute))
                model = v.get('id', None)
                if model and index:
                    app = uri.split('://')[0]
                    m = apps.get_model(app, model)
                    for v in m.objects.all():
                        indexvalue = getattr(v, index)
                        v_uri = urimanager.append(a_uri, value=indexvalue)
                        v_flag = _getflag(v_uri, Flag.AttrValue)
                        v_cns = [indexvalue]
                        routers.append(Router(
                            uri=v_uri,
                            flag=v_flag,
                            cns=v_cns
                        ))
            else:
                cns = []
            routers.append(Router(
                uri=a_uri,
                flag=flag,
                cns=cns
            ))
        return routers

    with open(path, 'r') as f:
        d = yaml.load(f.read())
        app = d.get('app', None)
        if not app:
            raise ValueError('yaml 必须指定 app')
        routers = []
        for k, v in d.items():
            if k == 'app':
                continue
            # 选出实体
            entity = v.get('entity', False)
            if entity is False:
                continue
            uri = urimanager.setschema(v['id'], app)
            index = v.get('index', None)
            uri = urimanager.setindex(uri, index)
            flag = _getflag(uri, Flag.Entity)
            cns = v.get('cn', [])
            # 实体类
            routers.append(Router(
                uri=uri,
                flag=flag,
                cns=cns
            ))
            # 属性
            attribute = v.get('attribute', None)
            if attribute:
                routers.extend(traverse_attr(uri, attribute))
            # 实体
            entity = apps.get_model(app, v['id'])
            for e in entity.objects.all():
                indexvalue = getattr(e, index)
                e_uri = urimanager.append(uri, value=indexvalue)
                e_flag = _getflag(e_uri, Flag.EntityIndex)
                e_cns = [indexvalue]
                routers.append(Router(
                    uri=e_uri,
                    flag=e_flag,
                    cns=e_cns
                ))
        Router.objects.bulk_create(routers)


def generate_dic(path):
    """
    生成领域词汇字典供 jieba 使用
    """
    word_frequency = 233333
    tag = DOMAIN_WORD_FLAG
    with open(path, 'w') as f:
        for e in Router.objects.distinct('cns'):
            for cn in e.cns:
                line = '%s %s %s\n' % (cn, word_frequency, tag)
                f.write(line)


def register_signs(path):
    """注册 signs, 如 =, > 等等.

    :param path: yaml 地址
    """
    with open(path, 'r') as f:
        d = yaml.load(f.read())
        _sign_map.update(_flattendict(d))


def is_sign(word):
    return word in _sign_map


def getsign(word):
    try:
        return Sign(word)
    except ValueError:
        word = _sign_map.get(word, None)
        if word:
            return Sign(word)


def combinesigns(*signs):
    if len(signs) == 1:
        return signs[0]
    v = ''
    for sign in signs:
        v += sign.value
    try:
        sign = Sign(v)
    except ValueError:
        return None
    return sign


def register_attribute_extend(path):
    """注册 aggregate functions.

    :param path: yaml 地址
    """
    with open(path, 'r') as f:
        d = yaml.load(f.read())
        _attribute_extend_map.update(_flattendict(d))


def is_attribute_extend(word):
    return word in _attribute_extend_map


def get_attribute_extend(word):
    func = _attribute_extend_map.get(word, None)
    if func:
        return AttributeExtend(func)


def is_special_extension(extension):
    return extension in [AttributeExtend.Species.value]


def register_quantifier(path):
    with open(path, 'r') as f:
        d = yaml.load(f.read())
        for v in d['root']:
            _quantifier.add(v)


def is_quantifier(word):
    return word in _quantifier


def register_valuefilter(path):
    """注册 value filter.

    :param path: yaml 地址
    """
    with open(path, 'r') as f:
        d = yaml.load(f.read())
        for v in d.values():
            for e in v:
                _value_filter.add(e)


def is_value(word, flag):
    r = word not in _value_filter
    r = r and flag not in _value_filter
    r = r and flag not in [
        Flag.Entity.value,
        Flag.EntityIndex.value,
        Flag.Attribute.value,
    ]
    r = r and not is_sign(word)
    r = r and not is_attribute_extend(word)
    r = r and not is_quantifier(word)
    return r


def deduction(uri):
    d = {
        'moves:name.max': 'moves:name.count.max'
    }
    basename = urimanager.basename(uri)
    rs = d.get(basename, None)
    if rs:
        return urimanager.setbasename(uri, rs)
    else:
        return uri
