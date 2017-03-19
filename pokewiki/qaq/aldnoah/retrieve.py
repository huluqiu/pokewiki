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
        self.relation_map = {
            Query.Relation.Equal: '',
            Query.Relation.Great: '__gt',
            Query.Relation.GreatTE: '__gte',
            Query.Relation.Less: '__lt',
            Query.Relation.LessTE: '__lte',
            Query.Relation.Contain: '__contains',
            Query.Relation.In: '__in',
        }

    def retrieve(self, query: Query):
        try:
            md = getattr(models, query.model)
        except AttributeError:
            return None
        queryset = None
        for attribue, relate, value in query.conditions:
            negative = relate.name.startswith('Not')
            relate = Query.Relation[relate.name.replace('Not', '')]
            if relate in self.relation_map:
                d = {attribue + self.relation_map[relate]: value}
                if negative:
                    queryset = md.objects.exclude(**d)
                else:
                    queryset = md.objects.filter(**d)
        return queryset
