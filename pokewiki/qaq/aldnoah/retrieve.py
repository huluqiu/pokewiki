from .models import Query
from qaq import models


class Retrieve(object):

    """Docstring for Retrieve. """

    def __init__(self):
        """TODO: to be defined1. """

    def retrieve(self, query: Query):
        pass


class DjangoRetrieve(Retrieve):

    """Docstring for DjangoRetrieve. """

    def __init__(self):
        """TODO: to be defined1. """
        Retrieve.__init__(self)
        self.sign_map = {
            Query.Sign.Equal: '',
            Query.Sign.Great: '__gt',
            Query.Sign.GreatTE: '__gte',
            Query.Sign.Less: '__lt',
            Query.Sign.LessTE: '__lte',
            Query.Sign.Contain: '__contains',
            Query.Sign.In: '__in',
        }

    def retrieve(self, query: Query):
        try:
            md = getattr(models, query.model)
        except AttributeError:
            return None
        queryset = None
        for attribue, relate, value in query.conditions:
            negative = relate.name.startswith('Not')
            relate = Query.Sign[relate.name.replace('Not', '')]
            if relate in self.sign_map:
                d = {attribue + self.sign_map[relate]: value}
                if negative:
                    queryset = md.objects.exclude(**d)
                else:
                    queryset = md.objects.filter(**d)
        return queryset
