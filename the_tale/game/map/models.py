# coding: utf-8
import datetime
from django.db import models

from common.utils.enum import create_enum

MAP_STATISTICS = create_enum('MAP_STATISTICS', ( ('LOWLANDS', 0, u'низины'),
                                                 ('PLAINS', 1, u'равнины'),
                                                 ('UPLANDS', 2, u'возвышенности'),
                                                 ('DESERTS', 3, u'пустыни'),
                                                 ('GRASS', 4, u'луга'),
                                                 ('FORESTS', 5, u'леса'),) )


class MapInfo(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    turn_number = models.BigIntegerField(null=False, db_index=True)

    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

    terrain = models.TextField(null=False, default='[]')

    world = models.TextField(null=False, default='', blank=True)

    statistics = models.TextField(null=False, default='{}')
