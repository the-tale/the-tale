
from django.db import models

from django.contrib.postgres import fields as postgres_fields

from . import conf


class Account(models.Model):

    id = models.BigAutoField(primary_key=True)

    account = models.BigIntegerField()

    currency = models.PositiveIntegerField()
    amount = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        unique_together = (('account', 'currency'))


class Transaction(models.Model):

    id = models.BigAutoField(primary_key=True)

    state = models.IntegerField(db_index=True)

    lifetime = models.DurationField()

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'


class Operation(models.Model):

    id = models.BigAutoField(primary_key=True)

    transaction = models.BigIntegerField(db_index=True)

    account = models.BigIntegerField(db_index=True)

    currency = models.PositiveIntegerField()

    amount = models.IntegerField()

    type = models.CharField(max_length=conf.OPERATION_TYPE_NAME_LENGTH)

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operations'
