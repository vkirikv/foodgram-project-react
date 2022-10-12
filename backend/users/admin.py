from django.contrib import admin

from .models import Subscriptions, User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'first_name',
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)


admin.site.register(Subscriptions, SubscriptionAdmin)
# admin.site.register(CustomUserAdmin)

