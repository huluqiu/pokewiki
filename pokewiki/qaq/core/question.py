from .utils import Stack
from . import wordseg


def preprocess(question):
    """TODO: Docstring for prprocess.

    :question: 问题
    :returns: 分词结果

    """
    return wordseg.tag(question)


def infoextract(cuts):
    """TODO: Docstring for infoextract.

    :cuts: 分词后的数据
    :returns:
    {
        'cuts': '',
        'entities': [(s, v)]
        'properties': [(p, v), ...]
        'relations': []
    }

    """
    entities = []
    properties = []
    relations = []
    v_stack = Stack()
    p_stack = Stack()
    for word, flag in cuts:
        pre_flag = flag[0:2]
        if pre_flag == 'ws':
            entities.append((flag[2:], '?'))
        if pre_flag == 'wu':
            entities.append((flag[2:], word))
        if pre_flag == 'wr':
            relations.append((word, flag))

        if len(p_stack) == 0 and flag == 'wp':
            p_stack.push(word)
        elif pre_flag in ['wp', 'uj', 'ws']:
            if len(p_stack) > 0:
                properties.append((p_stack.pop(), v_stack.pop(('?',))[0]))
            if pre_flag == 'wp':
                p_stack.push(word)
        elif pre_flag == 'wv' or pre_flag not in ['v', 'p', 'r', 'wu', 'zg']:
            v_stack.push((word, flag))
    while len(p_stack) > 0:
        properties.append((p_stack.pop(), v_stack.pop(('?',))[0]))
    while len(v_stack) > 0:
        word, flag = v_stack.pop()
        p = {'wvtp': '属性', 'wvkd': '种类'}.get(flag, None)
        if p:
            properties.append((p, word))
    return {
        'cuts': str(cuts),
        'entities': entities,
        'properties': properties,
        'relations': relations
    }


def templatematch(question):
    pass


def speculate(question):
    pass


def analyze(question):
    question = infoextract(question)
    rs = templatematch(question)
    rs = speculate(question) if rs is None else None
    return rs
