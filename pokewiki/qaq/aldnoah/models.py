from enum import Enum


class Query(object):

    """Docstring for Query. """

    class Sign(Enum):
        Equal = '='
        Great = '>'
        GreatTE = '>='
        Less = '<'
        LessTE = '<='
        Contain = 'LIKE'
        In = 'IN'
        NotEqual = '!='
        NotGreat = '<='
        NotGreatTE = '<'
        NotLess = '>='
        NotLessTE = '>'
        NotContain = 'NOT LIKE'
        NotIn = 'NOT IN'

    def __init__(self, target=None, model=None, conditions=None):
        # 对应 select
        # eg: ['id', 'name_en']
        self.target = target
        # 对应 from
        # eg: 'Pokemon'
        self.model = model
        # 对应 where
        # eg: [('name', '=', '皮卡丘'), ...]
        self.conditions = conditions


class Question(object):

    """Docstring for Question. """

    def __init__(self, question):
        self.question = question
        self.segment = []
        self.query = None
        #  TODO: question_type #


class Answer(object):

    """Docstring for Answer. """

    def __init__(self, brief=None, entire=None):
        self.brief = brief
        self.entire = entire
