# coding: utf-8

from django.contrib import admin

from game.mobs.models import MobRecord


class MobRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'state', 'created_at', 'updated_at')

    list_filter= ('state',)


admin.site.register(MobRecord, MobRecordAdmin)
