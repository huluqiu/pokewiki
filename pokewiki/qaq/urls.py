from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from qaq import views

router = DefaultRouter()
router.register(r'pokemons', views.PokemonViewSet)
router.register(r'egggroups', views.EggGroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
