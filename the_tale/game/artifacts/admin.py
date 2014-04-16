# coding: utf-8

from django.contrib import admin

from the_tale.game.artifacts.models import ArtifactRecord


class ArtifactRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'state', 'type', 'power_type', 'created_at', 'updated_at')

    list_filter = ('state', 'type', 'power_type')


admin.site.register(ArtifactRecord, ArtifactRecordAdmin)
