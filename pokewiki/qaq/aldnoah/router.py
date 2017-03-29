import yaml
from django.apps import apps
from enum import Enum
import re

# uri: qaq://Pokemon:name
# uri: qaq://Pokemon:name='皮卡丘'/name_en

# uri: qaq://Move:name/power=max
# uri: qaq://Move:name/type='水'
# uri: qaq://Move:name/name_en

# uri: qaq://Pokemon/gen:id \ qaq://*/gen:id
# uri: qaq://Move/gen:id    /

# cn1 \
# cn2 - >flag - > url
# cn3 /

DOMAIN_WORD_FLAG = 'poke'

Router = apps.get_model('qaq', 'Router')

re_model = re.compile(r'(?<=://)\w+(?=:)')
re_wi = re.compile(r'\w+://\w+:(\w+)(=)(\w+)')
re_wa = re.compile(r'(\w+:?\w+)(\W*)(\w*)')


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


class Sign(Enum):
    Equal = '='
    Great = '>'
    GreatTE = '>='
    Less = '<'
    LessTE = '<='
    Contain = '@>'
    In = '<@'
    NotEqual = '!='
    NotContain = '!@>'
    NotIn = '!<@'


def is_domainword(flag):
    return flag == DOMAIN_WORD_FLAG


def match(uri1, uri2):
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
    return uri.split('://')[-1]


def lenofuri(uri):
    return len(getbody(uri).split('/'))


def getmodel(uri):
    return re_model.search(uri).group()


def getattribute(uri):
    uri = getbody(uri)
    uri = uri.split('/')
    if len(uri) == 1:
        uri = uri[0].split(':')[-1]
        attribute = re_wa.match(uri).groups()
    else:
        parent = ''
        for e in uri[1:-1]:
            if not parent:
                parent = e.split(':')[0]
            else:
                parent = '%s/%s' % (parent, e.split(':')[0])
        leaf = list(re_wa.match(uri[-1]).groups())
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


def _getflag(url, t: Flag):
    return t.value


def _seturivalue(uri, value):
    if not value:
        return uri
    return '%s=%s' % (uri, value)


def _appenduri(uri, path):
    if not path:
        return uri
    return '%s/%s' % (uri, path)


def _addindex(uri, index):
    if not index:
        return uri
    return '%s:%s' % (uri, index)


# 根据 yaml 配置, 注册 uri
def register(config):

    def traverse_attr(uri, attribute):
        routers = []
        for k, v in attribute.items():
            a_uri = _appenduri(uri, k)
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
                        v_uri = _seturivalue(a_uri, indexvalue)
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

    with open(config, 'r') as f:
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
                e_uri = _seturivalue(uri, indexvalue)
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
