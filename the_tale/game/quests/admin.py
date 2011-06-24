# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Quest, QuestMailDelivery

class QuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'created_at')

class QuestMailDeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_quest', 'hero', 'delivery_from', 'delivery_to')

admin.site.register(Quest, QuestAdmin)
admin.site.register(QuestMailDelivery, QuestMailDeliveryAdmin)
