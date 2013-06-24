# coding: utf-8

from django.contrib import admin

from game.actions import models


class MetaActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'percents', 'created_at')

    list_filter = ('type',)


class MetaActionMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'hero', 'role')

    list_filter = ('role',)


admin.site.register(models.MetaAction, MetaActionAdmin)
admin.site.register(models.MetaActionMember, MetaActionMemberAdmin)
