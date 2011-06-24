# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Hero, HeroAction

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'npc', 'alive', 'first', 'angel_id')

    def angel_id(self, obj): return obj.angel_id


class HeroActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hero_id', 'action_id')

    def hero_id(self, obj): return obj.hero_id
    def action_id(self, obj): return obj.action_id


admin.site.register(Hero, HeroAdmin)
admin.site.register(HeroAction, HeroActionAdmin)
