
from django.db import models


class Event(models.Model):

    id = models.BigAutoField(primary_key=True)

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_at_turn = models.BigIntegerField(db_index=True)

    class Meta:
        db_table = 'events'


class EventTag(models.Model):

    id = models.BigAutoField(primary_key=True)

    event = models.BigIntegerField(db_index=True)

    tag = models.BigIntegerField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_at_turn = models.BigIntegerField(db_index=True)

    class Meta:
        db_table = 'events_tags'
        unique_together = (('tag', 'event'),)
