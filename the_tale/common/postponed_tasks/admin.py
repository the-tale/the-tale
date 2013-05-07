# coding: utf-8

from django.contrib import admin

from common.postponed_tasks.models import PostponedTask

class PostponedTaskAdmin(admin.ModelAdmin):
    list_display = ('id',  'state', 'internal_type', 'internal_state', 'created_at', 'live_time')


admin.site.register(PostponedTask, PostponedTaskAdmin)
