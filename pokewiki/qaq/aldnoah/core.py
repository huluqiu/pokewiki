from .utils import Stack, LazyProperty
from . import wordseg
from copy import deepcopy


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


class Question(object):

    """Docstring for Question. """

    def __init__(self, question):
        self.question = question


class Aldnoah(object):

    """Aldnoah"""

    def __init__(self):
        self._preprocessors = []
        self._strategies = []
        self._retrieves = []
        self._answeregs = []
        self._answerfilters = []

    def add_preprocessor(self, preprocessor):
        self._preprocessors.append(preprocessor)
        return self

    def add_strategy(self, strategy):
        self._strategies.append(strategy)
        return self

    def add_retrieve(self, retrieve):
        self._retrieves.append(retrieve)
        return self

    def add_answereg(self, answereg):
        self._answeregs.append(answereg)
        return self

    def add_answerfilter(self, answerfilter):
        self._answerfilters.append(answerfilter)
        return self

    def answer(self, question):
        qobj = Question(question)
        # 预处理
        for preprocess in self._preprocessors:
            preprocess.process(qobj)

        # 各种策略分析
        self._strategies = sorted(self._strategies, key=lambda obj: obj.priority, reverse=True)
        qobjs = []
        pre_prority = self._strategies[0].priority
        for strategy in self._strategies:
            if qobjs and strategy.priority < pre_prority:
                break
            pre_prority = strategy.priority
            q = strategy.analyze(deepcopy(qobj))
            if q:
                qobjs.append(q)

        # 检索数据
        for qobj in qobjs:
            for retrieve in self._retrieves:
                retrieve.retrieve(qobj)

        # 回答
        answers = []
        for qobj in qobjs:
            for answereg in self._answeregs:
                answer = answereg.answer(qobj)
                if answer:
                    answers.append(answer)

        # 若有多种回答, 需过滤
        if len(answers) > 1:
            for answerfilter in self._answerfilters:
                answerfilter.filter(answers)
        return answers
