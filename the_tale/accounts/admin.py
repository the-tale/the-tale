# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Account

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

class UserAdmin(DjangoUserAdmin):
    list_display = ('id', 'username', 'is_staff', 'last_login')

admin.site.register(Account, AccountAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
