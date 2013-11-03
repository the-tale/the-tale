# coding: utf-8

from django.contrib import admin

from the_tale.game.models import Bundle, SupervisorTask, SupervisorTaskMember

class BundleAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'type')

class SupervisorTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'created_at')

class SupervisorTaskMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'account')

admin.site.register(Bundle, BundleAdmin)
admin.site.register(SupervisorTask, SupervisorTaskAdmin)
admin.site.register(SupervisorTaskMember, SupervisorTaskMemberAdmin)
