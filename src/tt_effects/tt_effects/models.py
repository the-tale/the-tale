
from django.db import models

from django.contrib.postgres import fields as postgres_fields


class Effect(models.Model):

    id = models.BigAutoField(primary_key=True)

    attribute = models.BigIntegerField()

    entity = models.BigIntegerField()

    data = postgres_fields.JSONField(default='{}')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'effects'
