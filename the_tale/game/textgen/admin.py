# coding: utf-8

from django.contrib import admin

from dext.utils import s11n

from .models import Template, Word

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id','type', 'text')

    list_filter = ('type', )

    def text(self, obj):
        return s11n.from_json(obj.data)['template']


class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'normalized','type', 'properties')

    list_filter = ('type', )


admin.site.register(Template, TemplateAdmin)
admin.site.register(Word, WordAdmin)

