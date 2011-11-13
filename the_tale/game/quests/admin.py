# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Quest, QuestChoice
from .prototypes import QuestPrototype

class QuestChoiceInline(admin.TabularInline):
    model = QuestChoice

class QuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'cmd_number', 'percents', 'created_at', 'hero')

    inlines = [QuestChoiceInline]

    def percents(self, instance):
        return QuestPrototype(model=instance).percents


admin.site.register(Quest, QuestAdmin)
