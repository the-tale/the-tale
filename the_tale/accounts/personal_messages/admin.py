# coding: utf-8
from django.contrib import admin

from accounts.personal_messages.models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'created_at')

admin.site.register(Message, MessageAdmin)
