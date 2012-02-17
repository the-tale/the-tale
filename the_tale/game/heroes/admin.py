# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Hero, ChooseAbilityTask

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alive', 'health', 'angel_id')

    def angel_id(self, obj): return obj.angel_id

class ChooseAbilityTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'ability_id', 'comment')


admin.site.register(Hero, HeroAdmin)
admin.site.register(ChooseAbilityTask, ChooseAbilityTaskAdmin)
