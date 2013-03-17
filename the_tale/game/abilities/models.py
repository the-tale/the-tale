# coding: utf-8

from django.db import models

class AbilitiesData(models.Model):

    hero = models.ForeignKey('heroes.Hero', null=False)

    help_available_at = models.BigIntegerField(null=False, default=0)
    arena_pvp_1x1_available_at = models.BigIntegerField(null=False, default=0)
    arena_pvp_1x1_leave_queue_available_at = models.BigIntegerField(null=False, default=0)
    building_repair_available_at = models.BigIntegerField(null=False, default=0)
