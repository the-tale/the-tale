# coding: utf-8

from django.contrib import admin

from portal.newspaper.models import NewspaperEvent


class NewspaperEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'type', 'created_at')

    list_filter= ('section', 'type')


admin.site.register(NewspaperEvent, NewspaperEventAdmin)
