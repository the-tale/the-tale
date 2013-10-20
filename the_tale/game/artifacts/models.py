# coding: utf-8

from django.db import models

from rels.django_staff import TableIntegerField

from common.utils.enum import create_enum

from game.balance import constants as c

from game.artifacts.relations import ARTIFACT_TYPE


ARTIFACT_RECORD_STATE = create_enum('ARTFACT_RECORD_STATE', ( ('ENABLED', 0, u'в игре'),
                                                              ('DISABLED', 1, u'вне игры'),) )

RARITY_TYPE = create_enum('RARITY_TYPE', (('NORMAL', 0, u'обычный'),
                                          ('RARE', 1, u'редкий'),
                                          ('EPIC', 2, u'очень редкий'),) )

RARITY_TYPE_2_PRIORITY = { RARITY_TYPE.NORMAL: c.NORMAL_LOOT_PROBABILITY,
                           RARITY_TYPE.RARE: c.RARE_LOOT_PROBABILITY,
                           RARITY_TYPE.EPIC : c.EPIC_LOOT_PROBABILITY  }

class ArtifactRecord(models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    editor = models.ForeignKey('accounts.Account', null=True, related_name='+', blank=True, on_delete=models.SET_NULL)

    type = TableIntegerField(relation=ARTIFACT_TYPE, relation_column='value')

    rarity = models.IntegerField(default=RARITY_TYPE.NORMAL, choices=RARITY_TYPE._CHOICES)

    state = models.IntegerField(null=False, default=ARTIFACT_RECORD_STATE.DISABLED, choices=ARTIFACT_RECORD_STATE._CHOICES)

    level = models.IntegerField(default=0)

    uuid = models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    name_forms = models.TextField(null=False)

    description = models.TextField(null=False, default=u'', blank=True)

    mob = models.ForeignKey('mobs.MobRecord', null=True, related_name='+', blank=True, on_delete=models.SET_NULL)

    class Meta:
        permissions = (("create_artifactrecord", u"Может предлагать артефакты"),
                       ("moderate_artifactrecord", u"Может утверждать артефакты"),)
