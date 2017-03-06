from rest_framework import viewsets
from qaq.models import Pokemon, EggGroup
from qaq import serializers


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class PokemonViewSet(MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = serializers.PokemonListSerializer
    serializer_action_classes = {
        'list': serializers.PokemonListSerializer,
        'retrieve': serializers.PokemonSerializer,
    }


class EggGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EggGroup.objects.all()
    serializer_class = serializers.EggGroupSerializer
