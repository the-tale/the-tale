
from django.db import models


class UniqueId(models.Model):

    id = models.BigAutoField(primary_key=True)

    key = models.CharField(max_length=256, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unique_ids'
