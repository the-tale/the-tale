# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Quest
from .prototypes import QuestPrototype

class QuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'cmd_number', 'percents', 'created_at', 'hero')

    def percents(self, instance):
        return QuestPrototype(model=instance).percents


admin.site.register(Quest, QuestAdmin)
