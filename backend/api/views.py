from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny,
)
from rest_framework.response import Response
from djoser.views import UserViewSet

from .permissions import IsOwnerOrReadOnly
from users.models import Subscriptions
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    AmountIngredient,
)
from .serializers import (
    CustomUserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    FavoriteRecipeSerializer,
    SubscribeSerializer,
)

User = get_user_model()


class SubscriptionsViewSet(UserViewSet):
    """
    Подписка на автора.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    additional_serializer = SubscribeSerializer

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """
        Получение информации об авторе.
        """
        user = request.user
        authors = Subscriptions.objects.filter(user=user)
        pages = self.paginate_queryset(authors)
        serializer = self.additional_serializer(
            pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, **kwargs):
        """
        Подписка на автора.
        """
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Вы не можете подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Subscriptions.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscribe = Subscriptions.objects.create(user=user, author=author)
            serializer = self.additional_serializer(
                subscribe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user == author:
                return Response(
                    {'errors': 'Имена пользователя и автора совпадают'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Subscriptions.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'У вас нет подписки на такого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Получение тэгов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Получение ингредиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Работа с рецептами: просмотр, добавление, редактирование и удаление.
    Добавление рецептов в избранное и в список покупок.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    additional_serializer = FavoriteRecipeSerializer

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от типа запроса.
        """
        if self.request.method in ['POST', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """
        Назначение пользователя, который делает запрос, автором рецепта.
        """
        serializer.save(author=self.request.user)

    def add_recipe(self, model, request, pk):
        """
        Добавление рецепта к списку избранных рецептов или списку покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = model.objects.create(user=request.user, recipe=recipe)
        serializer = FavoriteRecipeSerializer(instance,
                                              context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        """
        Удаление рецепта из списка избранных рецептов или списка покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            model.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsOwnerOrReadOnly,))
    def favorite(self, request, **kwargs):
        """
        Обработка запросов, связанная с добавлением или удалением рецептов
        из избранного списка рецептов.
        """
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request, kwargs.get('pk'))

    @action(detail=True, methods=['GET', 'POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        """
        Обработка запросов, связанная с добавлением или удалением рецептов
        из списка покупок.
        """
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request, kwargs.get('pk'))

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Вывод списка ингредиетов и их количества в формат txt из
        списка покупок.
        """
        user = self.request.user
        ingredients = AmountIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_sum=Sum('amount')
        )
        filename = f'{user.username}_shopping_list'
        temp_shopping_cart = {}
        for ingredient in ingredients:
            name = ingredient[0]
            temp_shopping_cart[name] = {
                'amount': ingredient[2],
                'measurement_unit': ingredient[1]
            }
            shopping_cart = ["Список покупок\n\n"]
            for key, value in temp_shopping_cart.items():
                shopping_cart.append(f'{key} - {value["amount"]} '
                                     f'{value["measurement_unit"]}\n')
        response = HttpResponse(
            shopping_cart, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={filename}.txt'
        )
        return response
