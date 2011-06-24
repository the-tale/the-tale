# -*- coding: utf-8 -*-

from django.contrib import admin

from . import models

class ActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'percents', 'created_at')

class ActionIdlenessAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_action_id', 'hero')

    def base_action_id(self, obj): return obj.base_action_id

class ActionQuestMailDeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_action_id', 'quest')

    def base_action_id(self, obj): return obj.base_action_id

class ActionMoveToAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_action_id', 'hero', 'destination', 'road')

    def base_action_id(self, obj): return obj.base_action_id

class ActionBattlePvE_1x1Admin(admin.ModelAdmin):
    list_display = ('id', 'base_action_id', 'hero', 'hero_initiative', 'npc', 'npc_initiative')

    def base_action_id(self, obj): return obj.base_action_id

class ActionResurrectAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_action_id', 'hero')

    def base_action_id(self, obj): return obj.base_action_id

admin.site.register(models.Action, ActionAdmin)
admin.site.register(models.ActionIdleness, ActionIdlenessAdmin)
admin.site.register(models.ActionQuestMailDelivery, ActionQuestMailDeliveryAdmin)
admin.site.register(models.ActionMoveTo, ActionMoveToAdmin)
admin.site.register(models.ActionBattlePvE_1x1, ActionBattlePvE_1x1Admin)
admin.site.register(models.ActionResurrect, ActionResurrectAdmin)
