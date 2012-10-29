# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import Account, RegistrationTask, ChangeCredentialsTask, Award

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'nick', 'is_fast', 'email')

    def email(self, obj):
        return obj.user.email

class UserAdmin(DjangoUserAdmin):
    list_display = ('id', 'email', 'username', 'is_staff', 'last_login')

class RegistrationTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account')
    list_filter= ('state',)

class ChangeCredentialsTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account', )
    list_filter= ('state',)

class AwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'type', 'created_at')
    list_filter= ('type',)

admin.site.register(Account, AccountAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(RegistrationTask, RegistrationTaskAdmin)
admin.site.register(ChangeCredentialsTask, ChangeCredentialsTaskAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
