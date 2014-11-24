# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game.companions import relations


class CompanionRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    state = RelationIntegerField(relation=relations.COMPANION_RECORD_STATE, db_index=True)

    data = models.TextField(null=False, default='{}')

    class Meta:
        permissions = (("create_companionrecord", u"Может создавать спутников"),
                       ("moderate_companionrecord", u"Может утверждать спутников"),)
