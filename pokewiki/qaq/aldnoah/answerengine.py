from .models import Question, Answer, QuestionType


class AnswerEngine(object):

    """Docstring for AnswerEngine. """

    def answer(self, qobj, querysets):
        return Answer()


class DjangoAnswerEngine(AnswerEngine):

    """Docstring for PokeAnswerEngine. """

    def __init__(self):
        AnswerEngine.__init__(self)

    def answer(self, qobj: Question, queryset):
        if qobj.type is QuestionType.Bool:
            if queryset:
                answer = '对^_^'
            else:
                answer = '不不不→_→'
        elif qobj.type is QuestionType.Specific:
            answer = queryset
        else:
            answer = queryset
        return {
            'question': qobj.question,
            'answer': answer,
            # 'query': {
                # 'target': qobj.query.target,
                # 'condition': qobj.query.condition,
            # },
        }
