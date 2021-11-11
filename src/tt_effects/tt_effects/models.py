
from django.db import models


class Effect(models.Model):

    id = models.BigAutoField(primary_key=True)

    attribute = models.BigIntegerField()

    entity = models.BigIntegerField()

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'effects'
