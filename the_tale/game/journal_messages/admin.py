# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import MessagesLog, MessagePattern

class MessagePatternAdmin(admin.ModelAdmin):
    list_display = ('type', 'state', 'text', 'mask', 'author', 'editor')


admin.site.register(MessagesLog)
admin.site.register(MessagePattern, MessagePatternAdmin)
