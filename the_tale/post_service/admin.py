# coding: utf-8

from django.contrib import admin

from post_service.models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'created_at')
    list_filter= ('state',)


admin.site.register(Message, MessageAdmin)
