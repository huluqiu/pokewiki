from .models import Query
from . import urimanager
from .router import Sign, AttributeExtend
from qaq import models
from django.conf import settings
from django.db.models import (
    F, Max, Min, Avg, Count, Sum
)


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
            Sign.Equal: '',
            Sign.Great: '__gt',
            Sign.GreatTE: '__gte',
            Sign.Less: '__lt',
            Sign.LessTE: '__lte',
            Sign.Contain: '__contains',
            Sign.In: '__in',
        }
        self.extension_map = {
            AttributeExtend.Max.value: Max,
            AttributeExtend.Min.value: Min,
            AttributeExtend.Avg.value: Avg,
            AttributeExtend.Count.value: Count,
            AttributeExtend.Sum.value: Sum,
            AttributeExtend.Species.value: self.f_species,
        }

    def f_species(self, attribute):
        expression = (
            F('%s__hp' % attribute) +
            F('%s__attack' % attribute) +
            F('%s__defense' % attribute) +
            F('%s__sp_attack' % attribute) +
            F('%s__sp_defense' % attribute) +
            F('%s__speed' % attribute)
        )
        return expression

    def uri2attribute(self, uri):
        path = urimanager.path(uri, showschema=False, showindex=False)
        nodes = urimanager.split(path)
        attribute = ''
        if len(nodes) == 1:
            attribute = nodes[0]
        for node in nodes[1:]:
            attribute = urimanager.append(attribute, path=node)
        attribute = attribute.replace('/', '__')
        return attribute

    def sign2suffix(self, sign):
        sign = Sign(sign)
        negative = sign.name.startswith('Not')
        sign = Sign[sign.name.replace('Not', '')]
        sign = self.sign_map[sign]
        return sign, negative

    def retrieve(self, query: Query):
        try:
            md = getattr(models, query.model)
        except AttributeError:
            return None, None
        queryset = md.objects.all()
        annotate_dict = {}
        if settings.TESTING:
            annotate_list = []
            filter_list = []
            exclude_list = []
        # middle
        for uri, extension in query.middle:
            if extension not in self.extension_map:
                return
            expression = self.extension_map[extension]
            attribute = self.uri2attribute(uri)
            basename = urimanager.basename(uri, showindex=False, showextensions=False)
            middle_name = '%s_%s' % (extension, basename)
            annotate_dict[middle_name] = expression(attribute)
            if settings.TESTING:
                annotate_list.append((attribute, middle_name))
        if not settings.TESTING:
            queryset = queryset.annotate(**annotate_dict)
        # condition
        for uri, extension in query.condition:
            if not extension:
                path, sign, value = urimanager.separate(uri)
                attribute = self.uri2attribute(path)
                values = urimanager.valuesplit(value)
                if len(values) > 1:
                    attribute = '%s__in' % attribute
                    value = values
                sign, negative = self.sign2suffix(sign)
                attribute = attribute + sign
                lookup_dict = {attribute: value}
                if negative:
                    if settings.TESTING:
                        exclude_list.append((attribute, value))
                    else:
                        queryset = queryset.exclude(**lookup_dict)
                else:
                    if settings.TESTING:
                        filter_list.append((attribute, value))
                    else:
                        queryset = queryset.filter(**lookup_dict)
            else:
                # 目前只有 max 和 min 两种
                if extension in [AttributeExtend.Max.value, AttributeExtend.Min.value]:
                    expression = self.extension_map[extension]
                    basename = urimanager.basename(uri)
                    attribute = self.uri2attribute(uri)
                    key = '%s_%s' % (extension, basename)
                    if settings.TESTING:
                        value = key
                    else:
                        value = queryset.aggregate(**{key: expression(attribute)})[key]
                    lookup_dict = {attribute: value}
                    if settings.TESTING:
                        filter_list.append((attribute, value))
                    else:
                        queryset = queryset.filter(**lookup_dict)
        # target
        values = []
        aggregates = []
        for uri, extension in query.target:
            attribute = self.uri2attribute(uri)
            if not extension:
                values.append(attribute)
            else:
                expression = self.extension_map[extension]
                basename = urimanager.basename(uri)
                key = '%s_%s' % (extension, basename)
                if settings.TESTING:
                    rs = (attribute, extension)
                else:
                    rs = queryset.aggregate(**{key: expression(attribute)})
                aggregates.append(rs)
        if settings.TESTING:
            return None, {
                'annotate': annotate_list,
                'filter': filter_list,
                'exclude': exclude_list,
                'values': values,
                'aggregate': aggregates,
            }
        else:
            if values:
                values = queryset.values_list(*values).distinct()
                values = list(values)
            values.extend(aggregates)
            return queryset, values
