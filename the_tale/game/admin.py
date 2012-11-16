# -*- coding: utf-8 -*-

from django.contrib import admin

from game.models import Bundle, BundleMember, SupervisorTask, SupervisorTaskMember

class BundleAdmin(admin.ModelAdmin):
    list_display = ('id','owner', 'type')

class BundleMemberAdmin(admin.ModelAdmin):
    list_display = ('id','account')

class SupervisorTaskAdmin(admin.ModelAdmin):
    list_display = ('id','type', 'state', 'created_at')

class SupervisorTaskMemberAdmin(admin.ModelAdmin):
    list_display = ('id','task', 'account')

admin.site.register(Bundle, BundleAdmin)
admin.site.register(BundleMember, BundleMemberAdmin)
admin.site.register(SupervisorTask, SupervisorTaskAdmin)
admin.site.register(SupervisorTaskMember, SupervisorTaskMemberAdmin)
