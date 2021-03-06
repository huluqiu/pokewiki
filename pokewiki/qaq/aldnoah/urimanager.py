import re

_schema_flag = '://'
_path_flag = '/'
_index_flag = ':'
_extension_flag = '.'
_value_or_flag = '|'

_re_model = re.compile(r'(?<=://)\w+(?=:)')
_re_wi = re.compile(r'\w+://\w+:(\w+)(=)(\w+)')
_re_wa = re.compile(r'(\w+:?\w+(?:\.?\w+)*)(\W*)([\w|]*)')


def schema(uri):
    r = uri.split(_schema_flag)
    if len(r) == 1:
        return ''
    return r[0]


def setschema(uri, schema):
    if not schema:
        return uri
    path = uri.split(_schema_flag)[-1]
    return '%s%s%s' % (schema, _schema_flag, path)


def removeschema(uri):
    r = uri.split(_schema_flag)
    if len(r) > 1:
        uri = r[1]
    return uri


def split(uri):
    return uri.split(_path_flag)


def root(uri):
    s = schema(uri)
    uri = removeschema(uri)
    uri = uri.split(_path_flag)[0]
    return setschema(uri, s)


def separate(uri, showschema=True, showindex=True, showextensions=True):
    s = schema(uri)
    uri = removeschema(uri)
    nodes = uri.split(_path_flag)
    if len(nodes) == 1:
        path, sign, value = _re_wa.match(nodes[0]).groups()
        if not showextensions:
            path = path.split(_extension_flag)[0]
        if not showindex:
            path = path.replace(_index_flag, _path_flag)
        if showschema:
            path = setschema(path, s)
        return (path, sign, value)
    leaf = nodes[-1]
    leaf, sign, value = _re_wa.match(leaf).groups()
    if not showextensions:
        leaf = leaf.split(_extension_flag)[0]
    if not showindex:
        leaf = leaf.replace(_index_flag, _path_flag)
    path = ''
    for node in nodes[0:-1]:
        if not showindex:
            node = node.split(_index_flag)[0]
        # 路径中的 extension 会影响寻址
        node = node.split(_extension_flag)[0]
        path = '%s%s%s' % (path, node, _path_flag)
    path += leaf
    if showschema:
        path = setschema(path, s)
    return (path, sign, value)


def path(uri, **kwargs):
    return separate(uri, **kwargs)[0]


def basename(uri, showindex=True, **kwargs):
    p = path(uri, **kwargs).split(_path_flag)[-1]
    if not showindex:
        return p.split(_index_flag)[0]
    return p


def setbasename(uri, name):
    s = schema(uri)
    path, sign, value = separate(uri, showschema=False)
    nodes = path.split(_path_flag)
    if len(nodes) == 1:
        return s + _schema_flag + name + sign + value
    r = ''
    for node in nodes[0:-1]:
        r = r + node + _path_flag
    return s + _schema_flag + r + name + sign + value


def dirname(uri):
    s = schema(uri)
    p = path(uri, showschema=False)
    nodes = p.split(_path_flag)
    if len(nodes) == 1:
        return ''
    r = ''
    for node in nodes[0:-1]:
        r = r + node + _path_flag
    r = r[0:-1]
    return setschema(r, s)


def sign(uri):
    return separate(uri)[1]


def value(uri):
    return separate(uri)[2]


def valuecombine(uri, value):
    return '%s%s%s' % (uri, _value_or_flag, value)


def valuesplit(value):
    return value.split(_value_or_flag)


def related(uri1, uri2):
    uri1 = path(uri1).lower()
    uri2 = path(uri2).lower()
    return uri1 in uri2 or uri2 in uri1


def urilen(uri):
    uri = removeschema(uri)
    nodes = uri.split(_path_flag)
    return len(nodes)


def modelname(uri):
    return _re_model.search(uri).group()


def append(uri, path=None, sign=None, value=None):
    s = _path_flag
    if not uri:
        uri = ''
        s = ''
    if path:
        uri = '%s%s%s' % (uri, s, path)
    if sign:
        uri = '%s%s' % (uri, sign)
    if value:
        if not sign:
            uri = '%s%s' % (uri, '=')
        uri = '%s%s' % (uri, value)
    return uri


def index(uri):
    uri = basename(uri)
    nodes = uri.split(_index_flag)
    if nodes == 1:
        return ''
    return nodes[1]


def setindex(uri, index):
    if not index:
        return uri
    return '%s%s%s' % (uri, _index_flag, index)


def attribute_extensions(uri):
    uri = basename(uri)
    nodes = uri.split(_extension_flag)
    return nodes[1:]


def set_attribute_extension(uri, aevalue):
    if not aevalue:
        return uri
    return '%s%s%s' % (uri, _extension_flag, aevalue)
