# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Account

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

admin.site.register(Account, AccountAdmin)
