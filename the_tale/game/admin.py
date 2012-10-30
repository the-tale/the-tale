# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Bundle, BundleMember

class BundleAdmin(admin.ModelAdmin):
    list_display = ('id','owner', 'type')

class BundleMemberAdmin(admin.ModelAdmin):
    list_display = ('id','account')

admin.site.register(Bundle, BundleAdmin)
admin.site.register(BundleMember, BundleMemberAdmin)
