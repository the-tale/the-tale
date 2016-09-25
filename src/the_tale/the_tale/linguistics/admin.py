# coding: utf-8

from django.contrib import admin

from the_tale.linguistics import models


class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'normal_form', 'state', 'created_at', 'updated_at')
    list_filter = ('type', 'state',)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'state', 'author', 'raw_template', 'created_at', 'updated_at')
    list_filter = ('state', 'key')


class ContributionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'source', 'account', 'entity_id', 'created_at')
    list_filter = ('type',)


class RestrictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'external_id')
    list_filter = ('group',)


admin.site.register(models.Word, WordAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Contribution, ContributionAdmin)
admin.site.register(models.Restriction, RestrictionAdmin)
