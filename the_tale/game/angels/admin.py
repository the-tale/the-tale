# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Angel

class AngelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'energy')

    def angel_id(self, obj): return obj.angel_id


admin.site.register(Angel, AngelAdmin)
