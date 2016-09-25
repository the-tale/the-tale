# coding: utf-8

from django.contrib import admin

from the_tale.accounts.third_party.models import AccessToken


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'account', 'uid', 'created_at', 'application_name')
    list_filter = ('state',)



admin.site.register(AccessToken, AccessTokenAdmin)
