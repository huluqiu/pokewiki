from .utils import Stack
from .models import Question, Query
from enum import Enum


class Strategy(object):

    """Docstring for Strategy. """

    def __init__(self, priority=0):
        """TODO: to be defined1. """
        self.priority = priority

    def analyze(self, qobj):
        pass


# name domain recognition
class DomainWord(Enum):
    Entity = 'we'
    EntityIndex = 'wi'
    Attribute = 'wa'
    AttrValue = 'wv'
    Relation = 'wr'
    Sign = 'ws'


def ndr(flag):
    try:
        return DomainWord(flag[0:2])
    except ValueError:
        return None


def _popfromqueue(q, default=None):
    try:
        return q.popleft()
    except IndexError:
        return default


class InfoExtractStrategy(Strategy):

    """Docstring for InfoExtractStrategy. """

    def __init__(self, priority):
        Strategy.__init__(self, priority)
        self._ignorewords = [
            'uj',   # 的
            'wis',  # 是, 为
            'ry',   # 疑问代词: 谁, 什么, 哪, 哪些...
            'p',    # 介词
            'v',    # 动词
        ]

    def analyze(self, qobj: Question):
        wordcount = len(qobj.segment)
        for word, flag in qobj.segment:
            if flag in self._ignorewords:
                continue
            sign = ndr(flag)
        for i, e in enumerate(qobj.segment):
            word, flag = e
            if flag in self._ignorewords:
                continue
            sign = ndr(flag)
            """
            11: 弹出所有属性和实体
            10: 弹出实体
            01: 弹出一个属性
            00: 不操作
            """
            pop = '00'
            if sign in [DomainWord.Entity, DomainWord.EntityIndex]:
                if len(self._entityqueue) > 0:
                    pop = '11'
                self._entityqueue.append((word, flag))
            elif sign is DomainWord.Attribute:
                if len(self._attrqueue) > 0:
                    pop = '01'
                self._attrqueue.append((word, flag))
            elif sign is DomainWord.Relation:
                pass
            elif sign is DomainWord.AttrValue:
                self._valuequeue.append((word, flag))
            else:
                self._valuequeue.append((word, flag))

            if i == wordcount - 1:
                pop = '11'

            if pop == '11':
                entity = popfromqueue(self._entityqueue)
                attrcount = max(len(self._attrqueue, self._valuequeue))
                for i in range(attrcount):
                    attribue = popfromqueue(self._attrqueue)
                    value = popfromqueue(self._valuequeue)

        entities = []
        properties = []
        relations = []
        v_stack = Stack()
        p_stack = Stack()
        for word, flag in qobj.segment:
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
        qobj.entities = entities
        qobj.properties = properties
        qobj.relations = relations
        return qobj
