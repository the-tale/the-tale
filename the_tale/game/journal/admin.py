# coding: utf-8

from django.contrib import admin

from .models import Phrase

class PhraseAdmin(admin.ModelAdmin):
    list_display = ('id','type', 'template')

    list_filter = ('type', )


admin.site.register(Phrase, PhraseAdmin)

