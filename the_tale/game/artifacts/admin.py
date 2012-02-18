# coding: utf-8

from django.contrib import admin

from .models import ArtifactConstructor

class ArtifactConstructorAdmin(admin.ModelAdmin):
    list_display = ('id','uuid', 'item_type', 'equip_type', 'name')

    list_filter = ('item_type', 'equip_type')


admin.site.register(ArtifactConstructor, ArtifactConstructorAdmin)

