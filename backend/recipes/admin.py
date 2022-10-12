from django.contrib import admin
from django.contrib.admin import display

from .models import (
    Tag,
    Ingredient,
    AmountIngredient,
    Recipe,
    Favorite,
    ShoppingCart,
)


class AmountIngredientInline(admin.TabularInline):
    model = AmountIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (AmountIngredientInline,)
    list_display = (
        'name',
        'id',
        'author',
        'added_in_favorites',
    )
    readonly_fields = ('added_in_favorites',)
    list_filter = (
        'author',
        'name',
        'tags',
    )

    @display(description='Количество добавлений в избранное')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(AmountIngredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
