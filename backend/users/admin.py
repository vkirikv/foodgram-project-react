from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Subscriptions

admin.site.unregister(User)


class CustomUserAdmin(UserAdmin):
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
    list_display = (
        'user',
        'author',
    )


admin.site.register(Subscriptions, SubscriptionAdmin)
admin.site.register(User, CustomUserAdmin)

