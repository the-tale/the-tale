# coding: utf-8


from django.contrib import admin

from the_tale.statistics.models import Record

class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'date', 'value_int', 'value_float')
    list_filter = ('type',)

admin.site.register(Record, RecordAdmin)
