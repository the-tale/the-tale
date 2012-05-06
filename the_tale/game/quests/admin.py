# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Quest, QuestChoice, QuestsHeroes
from .prototypes import QuestPrototype

class QuestChoiceInline(admin.TabularInline):
    model = QuestChoice

class QuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'cmd_number', 'percents', 'created_at', 'hero')

    inlines = [QuestChoiceInline]

    def percents(self, instance):
        return QuestPrototype(model=instance).percents

    def hero(self, instance):
        heroes = QuestsHeroes.objects.filter(quest=instance.id).values_list('id', flat=True)
        if heroes:
            return heroes[0]
        return None


admin.site.register(Quest, QuestAdmin)
