from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from qaq import models, serializers
from qaq import aldnoahpoke


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class PokemonViewSet(MultiSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Pokemon.objects.all()
    serializer_class = serializers.PokemonListSerializer
    serializer_action_classes = {
        'list': serializers.PokemonListSerializer,
        'retrieve': serializers.PokemonSerializer,
    }


class EggGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.EggGroup.objects.all()
    serializer_class = serializers.EggGroupSerializer


@api_view()
def qaq(request):
    # q = request.query_params.get('question', None)
    return Response(aldnoahpoke.answer_test())
