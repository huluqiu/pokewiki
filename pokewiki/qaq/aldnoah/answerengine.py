from .models import Question, Answer


class AnswerEngine(object):

    """Docstring for AnswerEngine. """

    def answer(self, qobj, querysets):
        return Answer()


class DjangoAnswerEngine(AnswerEngine):

    """Docstring for PokeAnswerEngine. """

    def __init__(self):
        """TODO: to be defined1. """
        AnswerEngine.__init__(self)

    def answer(self, qobj: Question, querysets):
        return qobj
        # answer = []
        # for i, query in enumerate(qobj.queries):
            # queryset = querysets[i]
            # if len(query.target) == 1 and query.target == '*':
                # brief = list(queryset.values())
                # entire = brief
            # else:
                # brief = list(queryset.values(*query.target))
                # entire = list(queryset.values())
            # answer.append(Answer(brief, entire))
        # return answer
