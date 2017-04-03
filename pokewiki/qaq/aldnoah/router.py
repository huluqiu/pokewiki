import yaml
from django.apps import apps
from enum import Enum
import re

# uri: qaq://Pokemon:name
# uri: qaq://Pokemon:name='皮卡丘'
# uri: qaq://Move:name/name_en

# cn1 \
# cn2 - >flag - > url
# cn3 /

DOMAIN_WORD_FLAG = 'poke'

Router = apps.get_model('qaq', 'Router')

_re_model = re.compile(r'(?<=://)\w+(?=:)')
_re_wi = re.compile(r'\w+://\w+:(\w+)(=)(\w+)')
_re_wa = re.compile(r'(\w+:?\w+)(\W*)(\w*)')

_sign_map = {}

_aggregatefunc_map = {}

_value_filter = set()


class Flag(Enum):
    Entity = 'we'
    EntityIndex = 'wi'
    Attribute = 'wa'
    Value = 'wv'
    AttrValue = 'wav'
    Relation = 'wr'
    Sign = 'ws'
    Paired = 'wp'
    Any = '*'
    De = '的'


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


class AggregateFunc(Enum):
    Avg = 'avg'
    Count = 'count'
    Max = 'max'
    Min = 'min'
    Sum = 'sum'


def is_domainword(flag):
    return flag == DOMAIN_WORD_FLAG


def match(uri1, uri2):
    """判断 uri1 和 uri2 是否有关.

    有关: qaq://Pokemon:name 和 qaq://Pokemon:name/moves:name
    无关: qaq://Move:name 和 qaq://Ability:name
    """
    uri1 = getbody(uri1).lower().split('=')[0]
    uri2 = getbody(uri2).lower().split('=')[0]
    return uri1 in uri2 or uri2 in uri1


def geturi(word):
    """
    从数据库中查询单词对应的 uri 和 flag, 可能多个

    @return: [(uri, flag)]
    """
    queryset = Router.objects.filter(cns__contains=[word])
    return list(queryset.values('uri', 'flag'))


def getbody(uri):
    """返回去掉 schema 的 uri."""
    return uri.split('://')[-1]


def lenofuri(uri):
    return len(getbody(uri).split('/'))


def getmodel(uri):
    return _re_model.search(uri).group()


def getattribute(uri):
    """返回 uri 中的属性、sign和值(如果有sign和值).

    uri: qaq://Pokemon:name=皮卡丘
    return: (name, =, 皮卡丘)

    uri: qaq://Pokemon:name
    return: (name)
    """
    uri = getbody(uri)
    uri = uri.split('/')
    if len(uri) == 1:
        uri = uri[0].split(':')[-1]
        attribute = _re_wa.match(uri).groups()
    else:
        parent = ''
        for e in uri[1:-1]:
            if not parent:
                parent = e.split(':')[0]
            else:
                parent = '%s/%s' % (parent, e.split(':')[0])
        leaf = list(_re_wa.match(uri[-1]).groups())
        leaf[0] = leaf[0].replace(':', '/')
        if parent:
            leaf[0] = '%s/%s' % (parent, leaf[0])
        attribute = leaf
    attribute = list(filter(lambda n: n, attribute))
    return attribute


def getschema(uri):
    return uri.split('://')[0]


def setschema(uri, schema):
    if not schema:
        return uri
    separate = '://'
    path = uri.split(separate)[-1]
    return '%s://%s' % (schema, path)


def appenduri(uri, path=None, sign=None, value=None):
    if path:
        uri = '%s/%s' % (uri, path)
    if sign:
        if not isinstance(sign, Sign):
            raise TypeError('sign must be Sign, but %s', sign)
        uri = '%s%s' % (uri, sign.value)
    if value:
        if not sign:
            uri = '%s%s' % (uri, Sign.Equal.value)
        uri = '%s%s' % (uri, value)
    return uri


def _getflag(url, t: Flag):
    return t.value


def _addindex(uri, index):
    if not index:
        return uri
    return '%s:%s' % (uri, index)


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
            a_uri = appenduri(uri, path=k)
            flag = _getflag(a_uri, Flag.Attribute)
            if isinstance(v, list):
                # 属性值
                cns = v
            elif isinstance(v, dict):
                # 属性对象
                cns = v.get('cn', [])
                index = v.get('index', None)
                if index:
                    a_uri = _addindex(a_uri, index)
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
                        v_uri = appenduri(a_uri, value=indexvalue)
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
            uri = setschema(v['id'], app)
            index = v.get('index', None)
            uri = _addindex(uri, index)
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
                e_uri = appenduri(uri, value=indexvalue)
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


def register_aggregate(path):
    """注册 aggregate functions.

    :param path: yaml 地址
    """
    with open(path, 'r') as f:
        d = yaml.load(f.read())
        _aggregatefunc_map.update(_flattendict(d))


def is_aggregatefunc(word):
    return word in _aggregatefunc_map


def get_aggregatefunc(word):
    func = _aggregatefunc_map.get(word, None)
    if func:
        return AggregateFunc(func)


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
    r = r and not is_aggregatefunc(word)
    return r
