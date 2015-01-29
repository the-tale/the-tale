# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game import relations as game_relations

from the_tale.game.companions import relations


class CompanionRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    state = RelationIntegerField(relation=relations.STATE, db_index=True)
    type = RelationIntegerField(relation=relations.TYPE, db_index=True)
    dedication = RelationIntegerField(relation=relations.DEDICATION, db_index=True)
    rarity = RelationIntegerField(relation=relations.RARITY, db_index=True)
    archetype = RelationIntegerField(relation=game_relations.ARCHETYPE, null=True, default=None, blank=True)

    max_health = models.IntegerField(default=1)

    data = models.TextField(null=False, default='{}')

    class Meta:
        permissions = (("create_companionrecord", u"Может создавать спутников"),
                       ("moderate_companionrecord", u"Может утверждать спутников"),)
