from rest_framework import viewsets

from recipes.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Получение тэгов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Получение ингредиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
