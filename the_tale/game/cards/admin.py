# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Card

class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'cooldown_end', 'angel')

    def angel_id(self, obj): return obj.angel_id


admin.site.register(Card, CardAdmin)
