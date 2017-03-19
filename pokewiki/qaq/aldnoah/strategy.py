from .utils import Stack
from .models import Question


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
        self._stopwords = [
            'uj',   # 的
        ]
        self._ignorewords = []

    def analyze(self, qobj: Question):
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
