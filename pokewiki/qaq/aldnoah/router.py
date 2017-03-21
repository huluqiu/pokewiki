import yaml
from enum import Enum
from django.apps import apps

Router = apps.get_model('qaq', 'Router')

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


class Type(Enum):
    Entity = 'we'
    EntityIndex = 'wi'
    Attribute = 'wa'
    AttrValue = 'wv'
    Relation = 'wr'
    Sign = 'ws'


def match(entity, attribute):
    return False


def geturl(flag):
    return None


def getflag(url, t: Type):
    return t.value


def setschema(uri, schema):
    if not schema:
        return uri
    separate = '://'
    path = uri.split(separate)[-1]
    return '%s://%s' % (schema, path)


def seturivalue(uri, value):
    if not value:
        return uri
    return '%s=%s' % (uri, value)


def appenduri(uri, path):
    if not path:
        return uri
    return '%s/%s' % (uri, path)


def addindex(uri, index):
    if not index:
        return uri
    return '%s:%s' % (uri, index)


# 根据 yaml 配置, 注册 uri
def register(config):

    def traverse_attr(uri, attribute):
        routers = []
        for k, v in attribute.items():
            a_uri = appenduri(uri, k)
            flag = getflag(a_uri, Type.Attribute)
            if isinstance(v, list):
                # 属性值
                cns = v
            elif isinstance(v, dict):
                # 属性对象
                cns = v.get('cn', [])
                index = v.get('index', None)
                if index:
                    a_uri = addindex(a_uri, index)
                    flag = getflag(a_uri, Type.Attribute)
                attribute = v.get('attribute', None)
                if attribute:
                    routers.extend(traverse_attr(a_uri, attribute))
                model = v.get('id', None)
                entity = v.get('entity', None)
                if model and index and not entity:
                    app = uri.split('://')[0]
                    m = apps.get_model(app, model)
                    for v in m.objects.all():
                        indexvalue = getattr(v, index)
                        v_uri = seturivalue(a_uri, indexvalue)
                        v_flag = getflag(v_uri, Type.AttrValue)
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
            uri = addindex(uri, index)
            flag = getflag(uri, Type.Entity)
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
                e_uri = seturivalue(uri, indexvalue)
                e_flag = getflag(e_uri, Type.EntityIndex)
                e_cns = [indexvalue]
                routers.append(Router(
                    uri=e_uri,
                    flag=e_flag,
                    cns=e_cns
                ))
        Router.objects.bulk_create(routers)


def generate_dic(path):
    word_frequency = 2333
    with open(path, 'w') as f:
        for e in Router.objects.distinct('cns'):
            for cn in e.cns:
                line = '%s %s %s\n' % (cn, word_frequency, e.flag)
                f.write(line)
