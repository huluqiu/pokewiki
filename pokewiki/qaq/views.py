from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from qaq import models, serializers
from qaq.core import question


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
    questions = []
    rs = []
    with open('./pokewiki/qaq/core/questions', 'r') as f:
        questions = f.readlines()
        questions = list(map(lambda n: n.strip(), questions))

    for q in questions:
        cuts = question.preprocess(q)
        rs.append(question.infoextract(cuts))

    return Response(rs)

    # q = request.query_params.get('question', None)
    # if q is not None:
        # cuts = question.preprocess(q)
        # rs = question.infoextract(cuts)
        # return Response({'question': rs})
    # return Response()
