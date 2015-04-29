# coding: utf-8

from django.contrib import admin

from the_tale.game import models

class SupervisorTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'created_at')

class SupervisorTaskMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'account')

admin.site.register(models.SupervisorTask, SupervisorTaskAdmin)
admin.site.register(models.SupervisorTaskMember, SupervisorTaskMemberAdmin)
