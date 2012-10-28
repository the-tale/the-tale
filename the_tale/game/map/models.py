# coding: utf-8

from django.db import models


class MapInfo(models.Model):

    turn_number = models.BigIntegerField(null=False, db_index=True)

    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

    terrain = models.TextField(null=False, default='[]')

    terrain_percents = models.TextField(null=False, default='{}')
