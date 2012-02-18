# coding: utf-8

from django.contrib import admin

from .models import MobConstructor

class MobConstructorAdmin(admin.ModelAdmin):
    list_display = ('id','uuid', 'name')


admin.site.register(MobConstructor, MobConstructorAdmin)
