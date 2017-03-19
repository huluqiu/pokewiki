from .models import Question
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
        return qobj
