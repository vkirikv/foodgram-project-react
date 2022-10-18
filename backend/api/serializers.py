import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

from users.models import Subscriptions

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    AmountIngredient,
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """
    Получение информации о пользователе.
    """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Информация о подписке на данного автора.
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Регистрация пользователя.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }


class TagSerializer(serializers.ModelSerializer):
    """
    Получение информации о тэгах.
    """

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Получение информации об ингредиентах.
    """

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class Base64ImageField(serializers.ImageField):
    """
    Кастомный модуль с функциями кодирования и декодирования base64.
    """

    def to_internal_value(self, data):
        """
        Переопределение метода: если полученный объект строка, и эта строка
        начинается с 'data:image'...
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AmountIngredientSerializer(serializers.ModelSerializer):
    """
    Информация об ингредиенту и его количества в рецепте.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = AmountIngredient
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class AmountIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Создание сериализатора для записи количества ингредиента в рецепте
    при его создании.
    """
    id = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Получение информации о рецепте.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(
        many=True,
        source='recipes',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """
        Получение информации: добавлен ли рецепт в избранное.
        """
        user = self.context.get('request').user
        return (user.is_authenticated
                and Recipe.objects.filter(
                    favorites__user=user,
                    id=obj.id
                    ).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        """
        Получение информации: добавлен ли рецепт в список покупок.
        """
        user = self.context.get('request').user
        return (user.is_authenticated
                and Recipe.objects.filter(
                    shopping_cart__user=user,
                    id=obj.id,
                    ).exists()
                )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Создание рецепта.
    """

    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = AmountIngredientRecipeSerializer(
        source='recipes',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def ingredients_create(self, ingredients, recipe):
        """
        Добавление в рецепт ингредиента с указанием его количества.
        """
        ingredients_list = [
            AmountIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        ]
        AmountIngredient.objects.bulk_create(ingredients_list)

    def validate_ingredients(self, value):
        """
        Валидация ингредиентов.
        """
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError('Необходимо добавить '
                                              'ингридиет(ы)!')
        validated_ingredients = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            id_to_check = ingredient['id']
            ingredient_to_check = Ingredient.objects.filter(id=id_to_check)
            if not ingredient_to_check.exists():
                raise serializers.ValidationError(
                    'Ингридиента нет в базе!')
            if not isinstance(amount, (float, int)):
                raise serializers.ValidationError('Количество небходимо'
                                                  ' указать цифрами!')
            if amount <= 0:
                raise serializers.ValidationError('Количество ингредиента'
                                                  ' должно быть больше 0')
            ingredient_to_check = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            if ingredient_to_check in validated_ingredients:
                raise serializers.ValidationError('Ингредиенты не должны'
                                                  ' повторяться!')
            validated_ingredients.append(ingredient_to_check)
        return value

    def validate_tags(self, value):
        """
        Валидация тэгов.
        """
        tags = value
        if not tags:
            raise serializers.ValidationError('Добавьте хотя бы один тег')
        validated_tags = []
        for tag in tags:
            validated_tags.append(id)
        if len(validated_tags) != len(validated_tags):
            raise serializers.ValidationError('У одного рецепта может'
                                              ' быть только один тег.')
        return value

    def create(self, validated_data):
        """
        Добавление данных в поля  модели рецепта.
        """
        ingredients = validated_data.pop('recipes')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredients_create(
            ingredients=ingredients,
            recipe=recipe
        )
        return recipe

    def update(self, instance, validated_data):
        """
        Обновление полей модели рецепта.
        """
        # AmountIngredient.objects.filter(recipe=instance).delete()
        # tags = validated_data.pop('tags')
        # ingredients = validated_data.pop('recipes')
        # instance.tags.set(tags)
        # self.ingredients_create(
        #     ingredients=ingredients,
        #     recipe=instance
        # )
        # return super().update(instance=instance,
        # validated_data=validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipes')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredients_create(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        """
        Получение информации: добавлен ли рецепт в избранное.
        """
        user = self.context.get('request').user
        return (user.is_authenticated
                and Recipe.objects.filter(
                    favorites__user=user,
                    id=obj.id,
                    ).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        """
        Получение информации: добавлен ли рецепт в список покупок.
        """
        user = self.context.get('request').user
        return (user.is_authenticated
                and Recipe.objects.filter(
                    shopping_cart__user=user,
                    id=obj.id,
                    ).exists()
                )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Получение информации об избранных рецептов.
    """

    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """
    Получение полей модели рецепта для информации о рецептах автора,
    на которого подписан пользователь.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeSerializer(CustomUserSerializer):
    """
    Получение полной информации об авторе, на которого подписан пользователь.
    """

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Subscriptions
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        """
        Информация о подписке на данного пользователя.
        """
        return Subscriptions.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Получение рецептов автора."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSubscribeSerializer(queryset, many=True).data
