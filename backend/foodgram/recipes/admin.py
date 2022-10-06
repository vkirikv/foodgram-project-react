from django.contrib import admin

from .models import Tag, Ingredient, AmountIngredient, Recipe, Favorite

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(AmountIngredient)
admin.site.register(Recipe)
admin.site.register(Favorite)
