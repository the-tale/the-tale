# coding: utf-8
from django.db import models

from rels.django import RelationIntegerField

from the_tale.statistics import relations


class Record(models.Model):

    date = models.DateTimeField(null=False)
    type = RelationIntegerField(relation=relations.RECORD_TYPE, db_index=True)

    value_int = models.BigIntegerField()
    value_float = models.FloatField()
