# coding: utf-8

from django.db import models


class Message(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    recipient = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)
    sender = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)

    text = models.TextField(null=False, blank=True, default='')

    hide_from_sender = models.BooleanField(default=False)
    hide_from_recipient = models.BooleanField(default=False)
