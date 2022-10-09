from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet

app_name = 'api'

router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
# router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
