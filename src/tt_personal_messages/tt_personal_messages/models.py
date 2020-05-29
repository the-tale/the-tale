
from django.db import models
from django.contrib.postgres import fields as postgres_fields


class Account(models.Model):
    id = models.PositiveIntegerField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    new_messages_number = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'accounts'


class Message(models.Model):

    id = models.BigAutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    body = models.TextField(blank=True, default='')

    # just information fields
    sender = models.PositiveIntegerField()
    recipients = postgres_fields.ArrayField(models.PositiveIntegerField())

    class Meta:
        db_table = 'messages'


class Conversation(models.Model):
    id = models.BigAutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # composite conversation key has two parts:
    # - lowest account id (sender or recipient)
    # - highest account id (recipient or sender)
    account_1 = models.PositiveIntegerField()
    account_2 = models.PositiveIntegerField()

    message = models.ForeignKey(Message, related_name='+', on_delete=models.CASCADE, db_column='message')

    class Meta:
        db_table = 'conversations'
        unique_together = (('account_1', 'account_2', 'message'),)


class Visibility(models.Model):

    id = models.BigAutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    account = models.PositiveIntegerField()
    message = models.ForeignKey(Message, related_name='+', on_delete=models.CASCADE, db_column='message')

    visible = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'visibilities'
        unique_together = (('account', 'message'),)
        index_together = (('account', 'visible'),)
