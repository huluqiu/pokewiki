from .models import Question, Answer, QuestionType
from qaq.serializers import DomainCellSerializer
from django.conf import settings


class AnswerEngine(object):

    """Docstring for AnswerEngine. """

    def answer(self, qobj, querysets):
        return Answer()


class DjangoAnswerEngine(AnswerEngine):

    """Docstring for PokeAnswerEngine. """

    def __init__(self):
        AnswerEngine.__init__(self)

    def answer(self, qobj: Question, queryset, values):
        if qobj.type is QuestionType.Bool.value:
            if queryset:
                answer = '对^_^'
            else:
                answer = '不不不→_→'
        elif qobj.type is QuestionType.Specific.value:
            answer = values
        else:
            answer = values
        if settings.TESTING:
            answer = values
        return {
            'question': qobj.question,
            # 'segment': str(qobj.segment),
            # 'cells': [DomainCellSerializer(cell).data for cell in qobj.domaincells],
            # 'type': qobj.type,
            # 'query': {
                # 'middle': qobj.query.middle,
                # 'target': qobj.query.target,
                # 'condition': qobj.query.condition,
            # },
            'answer': answer,
        }
