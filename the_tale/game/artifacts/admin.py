# coding: utf-8

from django.contrib import admin

from game.artifacts.models import ArtifactRecord


class ArtifactRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'state', 'created_at', 'updated_at')

    list_filter = ('state',)


admin.site.register(ArtifactRecord, ArtifactRecordAdmin)
