
from django.db import models

from django.contrib.postgres import fields as postgres_fields


class Timer(models.Model):
    id = models.BigAutoField(primary_key=True)

    owner = models.BigIntegerField()
    entity = models.BigIntegerField()
    type = models.IntegerField()

    speed = models.FloatField()

    resources = models.FloatField()
    border = models.FloatField()

    resources_at = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField()

    data = postgres_fields.JSONField(default='{}')

    restarted = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timers'
        unique_together = [('owner', 'entity', 'type')]
