from .models import Question, Answer, QuestionType
from qaq.serializers import DomainCellSerializer


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
            'segment': str(qobj.segment),
            'cells': [DomainCellSerializer(cell).data for cell in qobj.domaincells],
            'type': qobj.type,
            'answer': answer,
            'query': {
                'middle': qobj.query.middle,
                'target': [DomainCellSerializer(cell).data for cell in qobj.query.target],
                'condition': [DomainCellSerializer(cell).data for cell in qobj.query.condition],
            },
        }
