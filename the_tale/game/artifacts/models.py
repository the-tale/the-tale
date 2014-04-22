# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game.artifacts import relations


class ArtifactRecord(models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    editor = models.ForeignKey('accounts.Account', null=True, related_name='+', blank=True, on_delete=models.SET_NULL)

    type = RelationIntegerField(relation=relations.ARTIFACT_TYPE, relation_column='value')
    power_type = RelationIntegerField(relation=relations.ARTIFACT_POWER_TYPE, relation_column='value')
    state = RelationIntegerField(relation=relations.ARTIFACT_RECORD_STATE, relation_column='value')

    rare_effect = RelationIntegerField(relation=relations.ARTIFACT_EFFECT, relation_column='value')
    epic_effect = RelationIntegerField(relation=relations.ARTIFACT_EFFECT, relation_column='value')

    level = models.IntegerField(default=0)

    uuid = models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    name_forms = models.TextField(null=False)

    description = models.TextField(null=False, default=u'', blank=True)

    mob = models.ForeignKey('mobs.MobRecord', null=True, related_name='+', blank=True, on_delete=models.SET_NULL)

    class Meta:
        permissions = (("create_artifactrecord", u"Может предлагать артефакты"),
                       ("moderate_artifactrecord", u"Может утверждать артефакты"),)
