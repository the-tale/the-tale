# coding: utf-8

from django.contrib import admin

from the_tale.game.mobs.models import MobRecord


class MobRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'archetype', 'state', 'created_at', 'updated_at')

    list_filter = ('state', 'archetype')


admin.site.register(MobRecord, MobRecordAdmin)
