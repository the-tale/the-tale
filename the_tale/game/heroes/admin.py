# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Hero

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alive', 'angel_id')

    def angel_id(self, obj): return obj.angel_id


admin.site.register(Hero, HeroAdmin)
