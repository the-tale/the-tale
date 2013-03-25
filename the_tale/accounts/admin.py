# coding: utf-8

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import Account, ChangeCredentialsTask, Award

class AccountAdmin(DjangoUserAdmin):
    list_display = ('id', 'email', 'nick', 'is_staff', 'last_login', 'created_at')
    ordering = ('-created_at',)

class ChangeCredentialsTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account', )
    list_filter= ('state',)

class AwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'type', 'created_at')
    list_filter= ('type',)

admin.site.register(Account, AccountAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(ChangeCredentialsTask, ChangeCredentialsTaskAdmin)
