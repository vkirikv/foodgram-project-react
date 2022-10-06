from django.contrib import admin

from .models import Tag, Ingredient, AmountIngredient, Recipe, Favorite


class AmountIngredientInline(admin.TabularInline):
    model = AmountIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (AmountIngredientInline,)


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(AmountIngredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
