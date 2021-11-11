
import uuid

from django.db import models

from . import conf


class Item(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.PositiveIntegerField(db_index=True)

    storage = models.IntegerField(default=0)

    data = models.JSONField(default=dict)

    base_type = models.CharField(max_length=conf.ITEM_TYPE_LENGTH)

    full_type = models.CharField(max_length=conf.ITEM_TYPE_LENGTH)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items'


class LogRecord(models.Model):
    id = models.BigAutoField(primary_key=True)

    transaction = models.UUIDField(default=uuid.uuid4)

    item = models.UUIDField()

    type = models.IntegerField()

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'log_records'
        index_together = [('item', 'created_at')]
