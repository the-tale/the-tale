# coding: utf-8


from django.db import models

from rels.django import TableIntegerField

from the_tale.post_service.relations import MESSAGE_STATE


class Message(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    processed_at = models.DateTimeField(null=True)

    state = TableIntegerField(relation=MESSAGE_STATE, relation_column='value', db_index=True)

    handler = models.TextField(default='')
