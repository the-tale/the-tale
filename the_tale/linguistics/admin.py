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
    list_display = ('id', 'type', 'account', 'entity_id')

    list_filter = ('type',)


admin.site.register(models.Word, WordAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Contribution, ContributionAdmin)
