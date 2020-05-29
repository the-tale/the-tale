
from django.db import models


class Property(models.Model):
    id = models.BigAutoField(primary_key=True)

    object_id = models.BigIntegerField()
    property_type = models.BigIntegerField()
    value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'properties'
        index_together = [('object_id', 'property_type')]
