from .models import Question


class Aldnoah(object):

    """Aldnoah"""

    def __init__(self):
        self._preprocessors = []
        self._strategies = []
        self._retrieve = None
        self._answereg = None

    def add_preprocessor(self, preprocessor):
        self._preprocessors.append(preprocessor)
        return self

    def add_strategy(self, strategy):
        self._strategies.append(strategy)
        self._strategies.sort(key=lambda e: e.priority, reverse=True)
        return self

    def set_retrieve(self, retrieve):
        self._retrieve = retrieve
        return self

    def set_answereg(self, answereg):
        self._answereg = answereg
        return self

    def answer(self, question, default=None):
        qobj = Question(question)
        # 预处理
        for preprocess in self._preprocessors:
            preprocess.process(qobj)

        # 按照策略的优先级进行分析
        for strategy in self._strategies:
            if qobj.queries:
                # 高优先级策略得到结果则不执行低优先级的
                break
            strategy.analyze(qobj)

        # 检索数据
        querysets = []
        for query in qobj.queries:
            queryset = self._retrieve.retrieve(query)
            querysets.append(queryset)

        # 回答
        answer = self._answereg.answer(qobj, querysets)

        return answer
