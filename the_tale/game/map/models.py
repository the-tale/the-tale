# coding: utf-8
import datetime

from django.db import models

class WorldInfo(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    data = models.TextField(null=False, default='', blank=True)


class MapInfo(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    turn_number = models.BigIntegerField(null=False, db_index=True)

    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

    terrain = models.TextField(null=False, default='[]')

    cells = models.TextField(null=False, default='')

    world = models.ForeignKey(WorldInfo, null=False, related_name='+', on_delete=models.CASCADE)

    statistics = models.TextField(null=False, default='{}')
