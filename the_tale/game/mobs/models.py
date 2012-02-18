# coding: utf-8

from django.db import models

class MobConstructor(models.Model):

    uuid = models.CharField(null=False, max_length=64, unique=True, db_index=True)
    
    name = models.CharField(null=False, default=u'', max_length=64)

    health_relative_to_hero = models.FloatField(null=False)
    
    initiative = models.FloatField(null=False)

    power_per_level = models.FloatField(null=False)

    damage_dispersion = models.FloatField(null=False)

    abilities = models.TextField(null=False, default='[]')

    loot_list = models.TextField(null=False, default='[]')
