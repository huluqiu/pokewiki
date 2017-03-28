from .models import Question
from . import router
import jieba
import jieba.posseg as pseg


class Preprocessor(object):

    """Docstring for Preprocessor. """

    def __init__(self):
        """TODO: to be defined1.

        :question: TODO

        """

    def process(self, qobj):
        return qobj


# 由于 jieba 的全局性，这里只用一个对象
class JiebaProcessor(Preprocessor):

    """jieba"""

    def __init__(self, path):
        Preprocessor.__init__(self)
        jieba.load_userdict(path)

    def process(self, qobj: Question):
        qobj.segment = pseg.cut(qobj.question, HMM=False)
        qobj.segment = [(word, flag) for (word, flag) in qobj.segment]


class DwrProcessor(Preprocessor):

    """领域词汇识别"""

    def __init__(self, flag):
        Preprocessor.__init__(self)
        self._flag = flag

    def process(self, qobj: Question):
        for word, flag in qobj.segment:
            if flag == self._flag:
                qobj.domainwords.append((word, router.geturi(word)))
