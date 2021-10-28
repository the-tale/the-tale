

from django.db import models

from django.contrib.postgres import fields as postgres_fields


class Diary(models.Model):

    id = models.PositiveIntegerField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    version = models.BigIntegerField(default=0)

    data = postgres_fields.JSONField(default=dict)

    class Meta:
        db_table = 'diaries'
