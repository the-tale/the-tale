# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

from game.balance import constants as c

ARTIFACT_RECORD_STATE = create_enum('ARTFACT_RECORD_STATE', ( ('ENABLED', 0, u'в игре'),
                                                              ('DISABLED', 1, u'вне игры'),) )

RARITY_TYPE = create_enum('RARITY_TYPE', (('NORMAL', 0, u'обычный'),
                                          ('RARE', 1, u'редкий'),
                                          ('EPIC', 2, u'эпичный'),) )

RARITY_TYPE_2_PRIORITY = { RARITY_TYPE.NORMAL: c.NORMAL_LOOT_PROBABILITY,
                           RARITY_TYPE.RARE: c.RARE_LOOT_PROBABILITY,
                           RARITY_TYPE.EPIC : c.EPIC_LOOT_PROBABILITY  }

ARTIFACT_TYPE = create_enum('ARTIFACT_TYPE', ( ('USELESS', 0, u'безделушка'),
                                               ('MAIN_HAND', 1, u'основная рука'),
                                               ('OFF_HAND', 2, u'вспомогательная рука'),
                                               ('PLATE', 3, u'броня'),
                                               ('AMULET', 4, u'амулет'),
                                               ('HELMET', 5, u'шлем'),
                                               ('CLOAK', 6, u'плащ'),
                                               ('SHOULDERS', 7, u'наплечники'),
                                               ('GLOVES', 8, u'перчатки'),
                                               ('PANTS', 9, u'штаны'),
                                               ('BOOTS', 10, u'сапоги'),
                                               ('RING', 11, u'кольцо') ) )

class ArtifactRecord(models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    editor = models.ForeignKey('accounts.Account', null=True, related_name='+')

    type = models.IntegerField(default=ARTIFACT_TYPE.USELESS, choices=ARTIFACT_TYPE._CHOICES)

    rarity = models.IntegerField(default=RARITY_TYPE.NORMAL, choices=RARITY_TYPE._CHOICES)

    state = models.IntegerField(null=False, default=ARTIFACT_RECORD_STATE.DISABLED, choices=ARTIFACT_RECORD_STATE._CHOICES)

    min_level = models.IntegerField(default=0)
    max_level = models.IntegerField(default=99999)

    uuid = models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    name_forms = models.TextField(null=False)

    description = models.TextField(null=False, default=u'')

    class Meta:
        permissions = (("create_artifactrecord", u"Может предлагать артефакты"),
                       ("moderate_artifactrecord", u"Может утверждать артефакты"),)
