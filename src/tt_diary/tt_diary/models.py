

from django.db import models


class Diary(models.Model):

    id = models.PositiveIntegerField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    version = models.BigIntegerField(default=0)

    data = models.JSONField(default=dict)

    class Meta:
        db_table = 'diaries'
