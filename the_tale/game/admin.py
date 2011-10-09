# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Time, Bundle, BundleMember

class TimeAdmin(admin.ModelAdmin):
    list_display = ('id','turn_number')

class BundleAdmin(admin.ModelAdmin):
    list_display = ('id','owner', 'type')

class BundleMemberAdmin(admin.ModelAdmin):
    list_display = ('id','angel')

admin.site.register(Time, TimeAdmin)
admin.site.register(Bundle, BundleAdmin)
admin.site.register(BundleMember, BundleMemberAdmin)
