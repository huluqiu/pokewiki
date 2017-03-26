from .models import Query
from . import router
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
        queryset = md.objects.all()
        condition = {}
        # filter
        for uri in query.condition:
            attribute, sign, value = router.getattribute(uri)
            # attribute: a/b/c/d -> a__b__c__d
            attribute = attribute.replace('/', '__')
            # sign: @> -> __contains
            sign = Query.Sign(sign)
            negative = sign.name.startswith('Not')
            sign = Query.Sign[sign.name.replace('Not', '')]
            sign = self.sign_map[sign]
            # (a/b, @>, v) -> a__b__contains=v
            attribute = attribute + sign
            if attribute in condition:
                pre_value = condition.pop(attribute)[0]
                if not isinstance(pre_value, list):
                    pre_value = [pre_value]
                pre_value.append(value)
                value = pre_value
                attribute = '%s__in' % attribute
            condition[attribute] = (value, negative)

        for k, v in condition.items():
            value, negative = v
            if negative:
                queryset = queryset.exclude(**{k: value})
            else:
                queryset = queryset.filter(**{k: value})

        # values
        values = []
        for uri in query.target:
            attribute = router.getattribute(uri)[0]
            attribute = attribute.replace('/', '__')
            values.append(attribute)
        return queryset.distinct().values(*values)
