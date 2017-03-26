from enum import Enum


class Query(object):

    """Docstring for Query. """

    class Sign(Enum):
        Equal = '='
        Great = '>'
        GreatTE = '>='
        Less = '<'
        LessTE = '<='
        Contain = '@>'
        In = '<@'
        NotEqual = '!='
        NotContain = '!@>'
        NotIn = '!<@'

    def __init__(self, model=None, target=None, condition=None):
        # 对应 from
        # eg: 'Pokemon'
        self.model = model
        # 对应 select
        # eg: ['id', 'name_en']
        self.target = target
        # 对应 where
        # eg: [('name', '=', '皮卡丘'), ...]
        self.condition = condition


class QuestionType(Enum):
    Bool = 'bool'
    Specific = 'specific'


class Question(object):

    """Docstring for Question. """

    def __init__(self, question):
        self.question = question
        self.segment = []
        self.domainwords = []
        self.type = None
        self.query = None


class Answer(object):

    """Docstring for Answer. """

    def __init__(self, brief=None, entire=None):
        self.brief = brief
        self.entire = entire
