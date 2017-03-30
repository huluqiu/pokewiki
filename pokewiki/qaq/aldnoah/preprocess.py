from .models import Question
import jieba
import jieba.posseg as pseg


class Preprocessor(object):

    """Docstring for Preprocessor. """

    def process(self, qobj):
        return qobj


# 由于 jieba 的全局性，这里只用一个对象
class JiebaProcessor(Preprocessor):

    """jieba"""

    def __init__(self, path):
        Preprocessor.__init__(self)
        jieba.load_userdict(path)
        self.jieba = jieba
        self._dynamicdic = [
            ('最多', None, 'a'),
        ]
        for word, freq, tag in self._dynamicdic:
            jieba.add_word(word, freq, tag)

    def process(self, qobj: Question):
        qobj.segment = pseg.cut(qobj.question, HMM=False)
        qobj.segment = [(word, flag) for (word, flag) in qobj.segment]
