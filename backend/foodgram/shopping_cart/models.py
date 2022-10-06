from django.db import models
from django.contrib.auth import get_user_model

from ..recipes.models import Recipe

User = get_user_model()


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name_plural = 'Рецепты для списка покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_follow'
            )
        ]
