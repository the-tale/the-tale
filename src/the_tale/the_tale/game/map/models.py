# coding: utf-8

from django.db import models

from django.contrib.postgres import fields as postgres_fields


class WorldInfo(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    data = models.TextField(null=False, default='', blank=True)


class MapInfo(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    turn_number = models.BigIntegerField(null=False, db_index=True)

    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

    terrain = models.TextField(null=False, default='[]')

    cells = models.TextField(null=False, default='')

    world = models.ForeignKey(WorldInfo, null=False, related_name='+', on_delete=models.CASCADE)

    statistics = models.TextField(null=False, default='{}')


class MapRegion(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    turn_number = models.BigIntegerField(null=False, unique=True)

    data = postgres_fields.JSONField()

    class Meta:
        index_together = (('turn_number', 'created_at'),)
