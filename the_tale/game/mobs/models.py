# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game import relations as game_relations

from the_tale.game.mobs.relations import MOB_RECORD_STATE, MOB_TYPE


class MobRecord(models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    editor = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    state = RelationIntegerField(relation=MOB_RECORD_STATE, db_index=True)
    type = RelationIntegerField(relation=MOB_TYPE, db_index=True)

    archetype = RelationIntegerField(relation=game_relations.ARCHETYPE, db_index=True)

    level = models.IntegerField(default=0)

    uuid = models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    description = models.TextField(null=False, default=u'')

    abilities = models.TextField(null=False)

    terrains = models.TextField(null=False)

    data = models.TextField(null=False, default='{}')

    class Meta:
        permissions = (("create_mobrecord", u"Может предлагать мобов"),
                       ("moderate_mobrecord", u"Может утверждать мобов"),)
