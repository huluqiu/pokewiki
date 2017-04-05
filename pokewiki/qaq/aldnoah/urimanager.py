import re

_schema_flag = '://'
_path_flag = '/'
_index_flag = ':'
_extension_flag = '.'

_re_model = re.compile(r'(?<=://)\w+(?=:)')
_re_wi = re.compile(r'\w+://\w+:(\w+)(=)(\w+)')
_re_wa = re.compile(r'(\w+:?\w+(?:\.?\w+)*)(\W*)(\w*)')


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


def separate(uri, showindex=True):
    uri = removeschema(uri)
    nodes = uri.split(_path_flag)
    if len(nodes) == 1:
        path, sign, value = _re_wa.match(nodes[0]).groups()
        if not showindex:
            path = path.replace(_index_flag, _path_flag)
        return (path, sign, value)
    leaf = nodes[-1]
    leaf, sign, value = _re_wa.match(leaf).groups()
    if not showindex:
        leaf = leaf.replace(_index_flag, _path_flag)
    path = ''
    for node in nodes[0:-1]:
        if not showindex:
            node = node.split(_index_flag)[0]
        path = '%s%s%s' % (path, node, _path_flag)
    path += leaf
    return (path, sign, value)


def path(uri):
    return separate(uri)[0]


def basename(uri):
    return path(uri).split(_path_flag)[-1]


def sign(uri):
    return separate(uri)[1]


def value(uri):
    return separate(uri)[2]


def related(uri1, uri2):
    uri1 = path(uri1).lower()
    uri2 = path(uri2).lower()
    return uri1 in uri2 or uri2 in uri1


def dirname(uri, showindex=True):
    uri = removeschema(uri)
    nodes = uri.split(_path_flag)
    if len(nodes) == 1:
        return ''
    if not showindex:
        nodes = [node.split(_index_flag)[0] for node in nodes]
    return nodes[0:-1]


def urilen(uri):
    uri = removeschema(uri)
    nodes = uri.split(_path_flag)
    return len(nodes)


def modelname(uri):
    return _re_model.search(uri).group()


def append(uri, path=None, sign=None, value=None):
    if path:
        uri = '%s%s%s' % (uri, _path_flag, path)
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
