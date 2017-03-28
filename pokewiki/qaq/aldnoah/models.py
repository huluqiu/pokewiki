from enum import Enum


class DomainCell(object):

    """Docstring for DomainCell. """

    def __init__(self, word, uri=None, flag=None):
        self.word = word
        self.uri = uri
        self.flag = flag


class QuestionType(Enum):
    Bool = 'bool'
    Specific = 'specific'


class Question(object):

    """Docstring for Question. """

    def __init__(self, question):
        self.question = question
        self.segment = None
        self.domaincells = None
        self.type = None
        self.query = None


class Query(object):

    """Docstring for Query. """

    def __init__(self, model=None, target=None, condition=None):
        # 对应 from
        # eg: 'Pokemon'
        self.model = model
        # 对应 select
        # eg: ['qaq://Pokemon:name/moves:name']
        self.target = target
        # 对应 where
        # eg: ['qaq://Pokemon:name=皮卡丘', 'qaq://Pokemon:name/moves:name/power=80']
        self.condition = condition


class Answer(object):

    """Docstring for Answer. """

    def __init__(self, brief=None, entire=None):
        self.brief = brief
        self.entire = entire
