from .utils import Stack
from .models import Question, Query
from enum import Enum
from .router import match
from collections import Iterable


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
            1: [
                ('wa',),
                ('wv',),
            ],
            2: [
                ('wa', '*'),
                ('*', 'wa')
            ],
            3: [
                ('wa', 'sign', '*'),
                ('*', '的', 'wa'),
            ],
        }
        # 不可能作为属性值的词性
        self._viflags = [
            'uj',   # 的
            'p',    # 介词
            'u',    # 助词
            'r',    # 代词
            'we', 'wi', 'wa',
        ]
        self._viwords = [
            '能', '系'
        ]
        # 代表赋值的词
        self._signs = {
            '=': ['是', '为', '等于'],
            '>': ['大于'],
            '<': ['小于'],
            '@>': ['包含', '包括', '有'],
        }
        # 展开符号字典
        flattensigns = {}
        for key, value in self._signs.items():
            for e in value:
                flattensigns[e] = key
        self._flattensigns = flattensigns

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
        domainwords_attr = list(filter(lambda n:
                                       n['flag'] == 'wa' or n['flag'] == 'wv',
                                       domainwords_filter))

        pairs = []
        if len(domainwords_attr) > 0:

            def patternmatch(segment, index, pattern, pairs):
                pattern = list(pattern)
                attribute = ''
                sign = ''
                value = ''
                for i, v in enumerate(pattern):
                    word, flag = segment[index + i]
                    if flag['match'] is True:
                        return False
                    if v == '*':
                        if (word in self._viwords or
                                flag['flag'] in self._viflags or
                                word in self._flattensigns.keys()):
                            return False
                        else:
                            value = word
                    elif v == 'sign':
                        if word not in self._flattensigns.keys():
                            return False
                        else:
                            sign = self._flattensigns[word]
                    else:
                        if word != v and flag['flag'] != v:
                            return False
                        else:
                            attribute = flag
                for word, flag in segment[index:index + len(pattern)]:
                    flag['match'] = True
                if attribute and sign and value:
                    pair = '%s%s%s' % (attribute['uri'], sign, value)
                elif attribute and value:
                    pair = '%s=%s' % (attribute['uri'], value)
                elif attribute:
                    if attribute['flag'] == 'wv':
                        pair = attribute['uri']
                    else:
                        pair = ''
                else:
                    pair = ''
                if pair:
                    pairs.append(pair)
                return True

            segment_domainflag = []
            domainwords_iter = iter(domainwords_filter)
            for word, flag in qobj.segment:
                if flag == 'poke':
                    flag = next(domainwords_iter)
                else:
                    flag = {'flag': flag}
                flag['match'] = False
                segment_domainflag.append((word, flag))

            allmatch = False
            patternkey = iter([3, 2, 1])
            while(not allmatch):
                try:
                    patterns = iter(self._pairpattern[next(patternkey)])
                except StopIteration:
                    break
                while(not allmatch):
                    try:
                        pattern = next(patterns)
                    except StopIteration:
                        break
                    index = 0
                    l_pattern = len(pattern)
                    while(index + l_pattern <= len(segment_domainflag)):
                        ismatch = patternmatch(segment_domainflag, index, pattern, pairs)
                        if ismatch:
                            index = index + l_pattern
                        else:
                            index = index + 1
                    # 检查是否全部配对
                    for v in domainwords_attr:
                        if v['match'] is False:
                            allmatch = False
                            break
                        else:
                            allmatch = True
        setattr(qobj, 'pairs', pairs)
