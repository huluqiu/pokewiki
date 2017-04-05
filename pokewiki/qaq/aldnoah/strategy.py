from .models import Question, Query, QuestionType, DomainCell
from .router import Flag, Sign, AttributeExtend
from . import router
from . import urimanager
import logging

logger = logging.getLogger(__name__)


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
        self._pairpattern = {}
        self._attribute_extend_pattern = {}

    def _add_pattern(self, patterndic, pattern):
        l = len(pattern)
        patterns = patterndic.get(l, None)
        if not patterns:
            patterns = []
            patterndic[l] = patterns
        patterns.append(pattern)

    def _elementtoflag(self, element):
        try:
            return Flag(element)
        except ValueError:
            return element

    def add_pairpattern(self, pattern):
        pattern = [self._elementtoflag(e) for e in pattern]
        # sign
        try:
            signindex = pattern.index(Flag.Sign)
        except ValueError:
            self._add_pattern(self._pairpattern, pattern)
        else:
            pattern_2sign = [e for e in pattern]
            pattern_2sign.insert(signindex, Flag.Sign)
            pattern_3sign = [e for e in pattern_2sign]
            pattern_3sign.insert(signindex, Flag.Sign)
            self._add_pattern(self._pairpattern, pattern)
            self._add_pattern(self._pairpattern, pattern_2sign)
            self._add_pattern(self._pairpattern, pattern_3sign)

    def add_attribute_extend_pattern(self, pattern):
        pattern = [self._elementtoflag(e) for e in pattern]
        self._add_pattern(self._attribute_extend_pattern, pattern)

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
                        if urimanager.related(uri_m['uri'], uri_n['uri']):
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
                    l1 = urimanager.urilen(uri_flags[max_index]['uri'])
                    l2 = urimanager.urilen(uri_flags[j]['uri'])
                    if l2 < l1:
                        max_index = j
            domaincells.append(
                DomainCell(
                    word=word,
                    uri=uri_flags[max_index]['uri'],
                    flag=uri_flags[max_index]['flag']
                )
            )
        domaincells = iter(domaincells)

        # 将 cells 替换到 segment 中
        def changetoblock(e):
            word, flag = e
            if router.is_domainword(flag):
                return next(domaincells)
            else:
                return e

        return list(map(changetoblock, segment))

    def _attribute_extend(self, blocks):
        """属性值扩展. """

        def ae_entity(block, **kwargs):
            if isinstance(block, DomainCell):
                if block.flag == Flag.Entity.value:
                    return True

        def ae_attribute(block, **kwargs):
            if isinstance(block, DomainCell):
                if block.flag == Flag.Attribute.value:
                    return True

        def ae_attribute_extend(block, **kwargs):
            if not isinstance(block, DomainCell):
                word, _ = block
                return router.is_attribute_extend(word)

        def ae_quantifier(block, **kwargs):
            if not isinstance(block, DomainCell):
                word, _ = block
                return router.is_quantifier(word)

        def ae_else(block, element, **kwargs):
            if not isinstance(block, DomainCell):
                word, flag = block
                return word == element or flag == element

        aefunc_map = {
            Flag.Entity: ae_entity,
            Flag.Attribute: ae_attribute,
            Flag.AttributeExtend: ae_attribute_extend,
            Flag.Quantifier: ae_quantifier,
            'else': ae_else,
        }

        def patternmatch(blocks, start, pattern):
            cell = None
            aeflag = None
            logger.debug('ae_pattern: %s', pattern)
            for index, element in enumerate(pattern):
                block = blocks[start + index]
                if isinstance(block, DomainCell):
                    cell = block
                    logger.debug('ae_cell: %s %s %s', cell.word, cell.uri, cell.flag)
                else:
                    word, flag = block
                    logger.debug('ae_ae: %s', word)
                    if router.is_attribute_extend(word):
                        aeflag = router.get_attribute_extend(word)
                aefunc = aefunc_map.get(element, ae_else)
                match = aefunc(
                    block=block,
                    element=element,
                )
                if not match:
                    logger.debug('not match')
                    return
            # 匹配成功
            logger.debug('match!!!!!!!!!!!!')
            cell.uri = urimanager.set_attribute_extension(cell.uri, aeflag.value)
            cell.uri = router.deduction(cell.uri)
            cell.flag = Flag.Attribute.value
            logger.debug('ae_pattern_match: %s, %s', cell.uri, cell.flag)
            return cell

        keys = list(self._attribute_extend_pattern.keys())
        keys.sort(reverse=True)
        for key in keys:
            for pattern in self._attribute_extend_pattern[key]:
                index = 0
                while(index + len(pattern) <= len(blocks)):
                    cell = patternmatch(blocks, index, pattern)
                    if cell:
                        del blocks[index: index + len(pattern)]
                        blocks.insert(index, cell)
                        index += 0
                    else:
                        index += 1
        return blocks

    def _pairing(self, blocks):
        """属性值配对. """
        signs = None

        def pair_attribute(word, flag, index, **kwargs):
            if flag == Flag.Attribute.value:
                return {'attribute': blocks[index]}

        def pair_sign(word, **kwargs):
            global signs
            if router.is_sign(word):
                if not signs:
                    signs = router.getsign(word)
                else:
                    sign = router.getsign(word)
                    signs = router.combinesigns(signs, sign)
                if signs:
                    return {'sign': signs.value}

        def pair_value(word, flag, index, **kwargs):
            if router.is_value(word, flag):
                if flag == Flag.AttrValue.value:
                    return {'value': blocks[index]}
                return {'value': word}

        def pair_av(flag, index, **kwargs):
            if flag == Flag.AttrValue.value:
                return {'value': blocks[index]}

        def pair_quantifier(word, **kwargs):
            if router.is_quantifier(word):
                return {'sign': '.count='}

        def pair_else(element, word, flag, **kwargs):
            if element == word or element == flag:
                return {}

        # 表驱动
        pairfunc_dict = {
            Flag.Attribute: pair_attribute,
            Flag.Sign: pair_sign,
            Flag.Value: pair_value,
            Flag.AttrValue: pair_av,
            Flag.Quantifier: pair_quantifier,
            'else': pair_else,
        }
        # 为每个 word 打上 match 标记
        match_flags = [False for _ in blocks]

        def patternmatch(blocks, start, pattern):
            global signs
            signs = None
            pairs = {}
            logger.debug('pattern: %s', pattern)
            for index, element in enumerate(pattern):
                if match_flags[start + index]:
                    return False
                block = blocks[start + index]
                if isinstance(block, DomainCell):
                    word = block.word
                    flag = block.flag
                else:
                    word, flag = block
                logger.debug('element: %s, word: %s, flag: %s', element, word, flag)
                pairfunc = pairfunc_dict.get(element, pair_else)
                logger.debug('func: %s', pairfunc)
                pair = pairfunc(
                    element=element,
                    word=word,
                    flag=flag,
                    index=start + index,
                )
                if pair is None:
                    logger.debug('not match, return!')
                    return False
                pairs.update(pair)
            # 没返回, 说明配对成功
            logger.debug('match!!!!!!!!!!!!!')
            logger.debug('pairs: %s', pairs)
            for i in range(start, start + len(pattern)):
                match_flags[i] = True
            attribute = pairs.get('attribute', None)
            sign = pairs.get('sign', Sign.Equal.value)
            value = pairs.get('value', None)
            if attribute and value:
                if isinstance(value, DomainCell):
                    uri = '%s%s%s' % (attribute.uri, sign, value.word)
                    value.flag = Flag.Value.value
                else:
                    uri = '%s%s%s' % (attribute.uri, sign, value)
                attribute.uri = uri
                logger.debug('uri: %s', attribute.uri)
                attribute.flag = Flag.Paired.value
                return True
            elif value:
                if sign:
                    value.uri = value.uri.replace('=', sign)
                value.flag = Flag.Paired.value
                return True
            return False
        keys = list(self._pairpattern.keys())
        keys.sort(reverse=True)
        domaincells = list(filter(lambda n: isinstance(n, DomainCell), blocks))
        for key in keys:
            for pattern in self._pairpattern[key]:
                index = 0
                len_pattern = len(pattern)
                while(index + len_pattern <= len(blocks)):
                    match = patternmatch(blocks, index, pattern)
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
        def is_maxormin(extension):
            return extension in [AttributeExtend.Max.value, AttributeExtend.Min.value]

        def solve_last(uri, extension, target, condition):
            dirname = urimanager.dirname(uri)
            dirname = (dirname, '')
            if dirname in target:
                if is_maxormin(extension):
                    condition.append((uri, extension))
                    target.append((uri, ''))
                else:
                    target.remove(dirname)
                    target.append((uri, extension))
            else:
                target.append((uri, extension))

        model = [urimanager.modelname(cell.uri) for cell in domaincells]
        model = model[0] if len(set(model)) == 1 else ''
        # 将 uri 根据 flag 归类
        flag_dict = {}
        for cell in domaincells:
            uris = flag_dict.get(cell.flag, None)
            if not uris:
                uris = []
                flag_dict[cell.flag] = uris
            uris.append(cell.uri)
        # 处理 Entity
        target = [(uri, '') for uri in flag_dict.get(Flag.Entity.value, [])]
        condition = []
        middle = []
        # 处理 EntityIndex
        uris = flag_dict.get(Flag.EntityIndex.value, [])
        for uri in uris:
            condition.append((uri, ''))
        # 处理 Attribute
        uris = flag_dict.get(Flag.Attribute.value, [])
        target.extend([(uri, '') for uri in uris if not urimanager.attribute_extensions(uri)])
        for uri in uris:
            extensions = urimanager.attribute_extensions(uri)
            if not extensions:
                continue
            uri = urimanager.path(uri, showextensions=False)
            if len(extensions) == 1:
                solve_last(uri, extensions[0], target, condition)
            else:
                extension = extensions[0]
                middle.append((uri, extension))
                basename = urimanager.basename(uri, showindex=False)
                middle_name = '%s_%s' % (extension, basename)
                rooturi = urimanager.root(uri)
                for index, extension in enumerate(extensions[1:]):
                    uri = urimanager.append(rooturi, path=middle_name)
                    middle_name = '%s_%s' % (extension, middle_name)
                    # 最后一个
                    if (index + 2) == len(extensions):
                        solve_last(uri, extension, target, condition)
                    else:
                        middle.append((uri, extension))
        # 处理 Pair
        uris = flag_dict.get(Flag.Paired.value, [])
        for uri in uris:
            extensions = urimanager.attribute_extensions(uri)
            if not extensions:
                condition.append((uri, ''))
                continue
            uri, sign, value = urimanager.separate(uri, showextensions=False)
            extension = extensions[0]
            middle.append((uri, extension))
            basename = urimanager.basename(uri, showindex=False)
            middle_name = '%s_%s' % (extension, basename)
            rooturi = urimanager.root(uri)
            uri = urimanager.append(rooturi, path=middle_name)
            for index, extension in enumerate(extensions[1:]):
                if (index + 2) == len(extensions):
                    break
                uri = urimanager.append(rooturi, path=middle_name)
                middle.append((uri, extension))
                middle_name = '%s_%s' % (extension, middle_name)
            uri = '%s%s%s' % (uri, sign, value)
            condition.append((uri, ''))
        # 处理 Relation
        uris = flag_dict.get(Flag.Relation.value, [])
        condition_paths = [urimanager.path(uri) for uri, _ in condition]
        for uri in uris:
            dirname = urimanager.dirname(uri)
            if uri not in condition_paths:
                if (uri, '') not in target:
                    target.append((uri, ''))
            elif dirname not in condition_paths:
                if (dirname, '') not in target:
                    target.append((dirname, ''))
            else:
                continue
        return Query(model, middle, target, condition)

    def _questiontype(self, query: Query):
        q = len(query.condition) == 1 and query.condition[0][1] == 'wi'
        if not query.target and not q:
            return QuestionType.Bool.value
        else:
            return QuestionType.Specific.value

    def analyze(self, qobj: Question):
        blocks = self._filteruri(qobj.segment)
        blocks = self._attribute_extend(blocks)
        qobj.domaincells = self._pairing(blocks)
        qobj.query = self._querygenerate(qobj.domaincells)
        qobj.type = self._questiontype(qobj.query)
