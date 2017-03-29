from .models import Question, Query, QuestionType, DomainCell
from .router import Flag, Sign
from . import router


class Strategy(object):

    """Docstring for Strategy. """

    def __init__(self, priority=0):
        """TODO: to be defined1. """
        self.priority = priority

    def analyze(self, qobj):
        pass


class InfoExtractStrategy(Strategy):

    """Docstring for InfoExtractStrategy. """

    def __init__(self, priority):
        Strategy.__init__(self, priority)
        # 属性值配对模式, key 代表窗口大小
        self._pairpattern = {
            1: [
                (Flag.AttrValue,),
            ],
            2: [
                (Flag.Attribute, Flag.Value),
                (Flag.Value, Flag.Attribute),
            ],
            3: [
                (Flag.Attribute, Flag.Sign, Flag.Value),
                (Flag.Value, '的', Flag.Attribute),
            ],
        }
        # 不可能作为属性值的词性
        self._viflags = [
            'uj',   # 的
            'p',    # 介词
            'u',    # 助词
            'r',    # 代词
            'c',    # 连词
            'we', 'wi', 'wa',
        ]
        self._viwords = [
            '能', '系'
        ]
        # 代表赋值的词
        self._signs = {
            '=': ['是', '为', '等于'],
            '>': ['大于'],
            '>=': ['大于等于', '不小于'],
            '<': ['小于'],
            '<=': ['小于等于', '不大于'],
            '@>': ['包含', '包括', '有'],
            '!=': ['不是', '不为', '不等于'],
            '!@>': ['不包含', '不包括', '没有'],
        }
        # 展开符号字典
        flattensigns = {}
        for key, value in self._signs.items():
            for e in value:
                flattensigns[e] = key
        self._flattensigns = flattensigns

    def _filteruri(self, segment):
        """筛选 uri 和 flag"""
        domainwords = []
        for word, flag in segment:
            if router.is_domainword(flag):
                domainwords.append((word, router.geturi(word)))
        # 为每个 uri 初始化权值
        weightss = [[0 for _ in uris] for word, uris in domainwords]
        # 计算每个 uri 的权值
        for i, uris_i in enumerate(domainwords):
            weights_i = weightss[i]
            for j, uris_j in enumerate(domainwords[i + 1:]):
                weights_j = weightss[i + 1 + j]
                for m, uri_m in enumerate(uris_i[1]):
                    for n, uri_n in enumerate(uris_j[1]):
                        if router.match(uri_m['uri'], uri_n['uri']):
                            weights_i[m] = weights_i[m] + 1
                            weights_j[n] = weights_j[n] + 1
        # 根据 uri 的权值筛选 uri
        # 规则: 权值大, uri 路径短
        domaincells = []
        for i, value in enumerate(domainwords):
            word, uri_flags = value
            weights = weightss[i]
            for j, weight in enumerate(weights):
                if j == 0:
                    max_index = j
                    max_weight = weights[j]
                    continue
                if weight > max_weight:
                    max_index = j
                    max_weight = weight
                elif weight == max_weight:
                    l1 = router.lenofuri(uri_flags[max_index]['uri'])
                    l2 = router.lenofuri(uri_flags[j]['uri'])
                    if l2 < l1:
                        max_index = j
            domaincells.append(
                DomainCell(
                    word=word,
                    uri=uri_flags[max_index]['uri'],
                    flag=uri_flags[max_index]['flag']
                )
            )
        return domaincells

    def _pairing(self, domaincells, segment):
        """属性值配对"""
        # segment 中 domainword 的位置到 domaincells 的映射
        seg2domain = list(filter(lambda n:
                                 router.is_domainword(segment[n][1]),
                                 range(len(segment))))

        def pair_attribute(word, flag, index, **kwargs):
            if flag == Flag.Attribute.value:
                return {'attribute': domaincells[seg2domain.index(index)]}

        def pair_sign(word, **kwargs):
            if word in self._flattensigns.keys():
                return {'sign': self._flattensigns[word]}

        def pair_value(word, flag, index, **kwargs):
            q_invalid_word = word not in self._viwords and word not in self._flattensigns.keys()
            q_invalid_flag = flag not in self._viflags
            if q_invalid_word and q_invalid_flag:
                if flag == Flag.AttrValue.value:
                    return {'value': domaincells[seg2domain.index(index)]}
                return {'value': word}

        def pair_av(flag, index, **kwargs):
            if flag == Flag.AttrValue.value:
                return {'value': domaincells[seg2domain.index(index)]}

        def pair_else(element, word, **kwargs):
            if element == word:
                return {}

        # 表驱动
        pairfunc_dict = {
            Flag.Attribute: pair_attribute,
            Flag.Sign: pair_sign,
            Flag.Value: pair_value,
            Flag.AttrValue: pair_av,
            'else': pair_else,
        }
        # 为每个 word 打上 match 标记
        match_flags = [False for _ in segment]

        def patternmatch(segment, start, pattern):
            pairs = {}
            for index, element in enumerate(pattern):
                if match_flags[start + index]:
                    return False
                word, flag = segment[start + index]
                if flag == router.DOMAIN_WORD_FLAG:
                    flag = domaincells[seg2domain.index(start + index)].flag
                pairfunc = pairfunc_dict.get(element, pair_else)
                pair = pairfunc(
                    element=element,
                    word=word,
                    flag=flag,
                    index=start + index,
                )
                if pair is None:
                    return False
                pairs.update(pair)
            # 没返回, 说明配对成功
            for i in range(start, start + len(pattern)):
                match_flags[i] = True
            attribute = pairs.get('attribute', None)
            sign = pairs.get('sign', Sign.Equal.value)
            value = pairs.get('value', None)
            if attribute and value:
                if isinstance(value, DomainCell):
                    uri = value.uri
                    value.flag = Flag.Value.value
                else:
                    uri = '%s%s%s' % (attribute.uri, sign, value)
                attribute.uri = uri
                attribute.flag = Flag.Paired.value
                return True
            elif value:
                value.flag = Flag.Paired.value
                return True
            return False

        patternkey = list(self._pairpattern.keys())
        patternkey.sort(reverse=True)
        for key in patternkey:
            patterns = self._pairpattern[key]
            for pattern in patterns:
                index = 0
                len_pattern = len(pattern)
                while(index + len_pattern <= len(segment)):
                    match = patternmatch(segment, index, pattern)
                    index += len_pattern if match else 1
                # 检查是否全配对
                cellsnotmatch = list(filter(lambda cell:
                                            cell.flag == Flag.Attribute.value or
                                            cell.flag == Flag.AttrValue.value,
                                            domaincells))
                if len(cellsnotmatch) == 0:
                    return list(filter(lambda cell:
                                       cell.flag != Flag.Value.value,
                                       domaincells))
        return list(filter(lambda cell:
                           cell.flag != Flag.Value.value,
                           domaincells))

    def _querygenerate(self, domaincells):
        """确定 model, target 和 condition"""
        model = list(map(lambda cell:
                         router.getmodel(cell.uri),
                         domaincells))
        model = model[0] if len(set(model)) == 1 else ''
        target = list(filter(lambda cell:
                             cell.flag == Flag.Attribute.value or
                             cell.flag == Flag.Entity.value,
                             domaincells))
        condition = list(filter(lambda cell:
                                cell.flag == Flag.AttrValue.value or
                                cell.flag == Flag.Paired.value or
                                cell.flag == Flag.EntityIndex.value,
                                domaincells))
        return Query(model, target, condition)

    def _questiontype(self, query: Query):
        q = len(query.condition) == 1 and query.condition[0].flag == 'wi'
        if not query.target and not q:
            return QuestionType.Bool
        else:
            return QuestionType.Specific

    def analyze(self, qobj: Question):
        domaincells = self._filteruri(qobj.segment)
        qobj.domaincells = self._pairing(domaincells, qobj.segment)
        qobj.query = self._querygenerate(qobj.domaincells)
        qobj.type = self._questiontype(qobj.query)
