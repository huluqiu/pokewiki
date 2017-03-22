from .utils import Stack
from .models import Question, Query
from enum import Enum
from .router import match


class Strategy(object):

    """Docstring for Strategy. """

    def __init__(self, priority=0):
        """TODO: to be defined1. """
        self.priority = priority

    def analyze(self, qobj):
        pass


def _popfromqueue(q, default=None):
    try:
        return q.popleft()
    except IndexError:
        return default


class InfoExtractStrategy(Strategy):

    """Docstring for InfoExtractStrategy. """

    def __init__(self, priority):
        Strategy.__init__(self, priority)
        # 属性值配对模式, key 代表窗口大小
        self._pairpattern = {
            1: [],
            2: [],
            3: [],
        }
        # 不可能作为属性值的词性
        self._viflags = [
            'uj',   # 的
            'ry',   # 疑问代词: 谁, 什么, 哪, 哪些...
            'p',    # 介词
            'u',    # 助词
            'we', 'wi', 'wa',
        ]
        self._viwords = [
            '是',
        ]
        # 代表赋值的词
        self._signs = [
            '是', '为',
            '等于', '大于', '小于',
            '有', '包括', '包含'
        ]

    def analyze(self, qobj: Question):
        # 1. 筛选 uri 和 flag
        # 2. 属性值配对
        # 3. 得出 conditions
        # 4. 确定 target 和 model
        # 5. 生成 query 放进 qobj
        domainwords_filter = []
        length = len(qobj.domainwords)
        weights = [[0 for e in range(len(uris))] for word, uris in qobj.domainwords]
        for i in range(length):
            uris1 = qobj.domainwords[i][1]
            weight1 = weights[i]
            for j in range(i + 1, length):
                uris2 = qobj.domainwords[j][1]
                weight2 = weights[j]
                for m, value1 in enumerate(uris1):
                    w1 = weight1[m]
                    for n, value2 in enumerate(uris2):
                        w2 = weight2[n]
                        if match(value1['uri'], value2['uri']):
                            weight1[m] = w1 + 1
                            weight2[n] = w2 + 1
                weights[j] = weight2
            weights[i] = weight1
        for i in range(length):
            word, uris = qobj.domainwords[i]
            weight = weights[i]
            index = 0
            for j, value in enumerate(weight):
                if j == index:
                    continue
                max_weight = weight[index]
                if value > max_weight:
                    index = j
                elif value == max_weight:
                    l1 = len(uris[index]['uri'].split('/'))
                    l2 = len(uris[j]['uri'].split('/'))
                    if l2 < l1:
                        index = j
            domainwords_filter.append({
                'word': word,
                'uri': uris[index]['uri'],
                'flag': uris[index]['flag']
            })
        qobj.domainwords = domainwords_filter

        # 2
