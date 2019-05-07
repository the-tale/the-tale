
from django.db import models

from django.contrib.postgres import fields as postgres_fields

from . import conf


class SellLot(models.Model):
    item_type = models.CharField(max_length=conf.ITEM_TYPE_NAME_LENGTH)
    item = models.UUIDField(primary_key=True)

    price = models.BigIntegerField()

    owner = models.BigIntegerField(null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sell_lots'
        index_together = (('item_type', 'price'),)


class LogRecord(models.Model):
    id = models.BigAutoField(primary_key=True)

    operation_type = models.IntegerField()

    lot_type = models.IntegerField()

    item_type = models.CharField(max_length=conf.ITEM_TYPE_NAME_LENGTH)
    item = models.UUIDField()

    owner = models.BigIntegerField(null=True)

    price = models.BigIntegerField()

    data = postgres_fields.JSONField(default='{}')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'log_records'
        index_together = (('operation_type', 'created_at'),)
