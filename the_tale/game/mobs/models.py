# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game import relations as game_relations

from the_tale.game.mobs import relations


class MobRecord(models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    editor = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    state = RelationIntegerField(relation=relations.MOB_RECORD_STATE, db_index=True)
    type = RelationIntegerField(relation=game_relations.BEING_TYPE, db_index=True)

    is_mercenary = models.BooleanField(default=False)
    is_eatable = models.BooleanField(default=False)

    archetype = RelationIntegerField(relation=game_relations.ARCHETYPE, db_index=True)

    level = models.IntegerField(default=0)

    uuid = models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    description = models.TextField(null=False, default=u'')

    abilities = models.TextField(null=False)

    terrains = models.TextField(null=False)

    data = models.TextField(null=False, default='{}')

    communication_verbal = RelationIntegerField(relation=game_relations.COMMUNICATION_VERBAL, db_index=True)
    communication_gestures = RelationIntegerField(relation=game_relations.COMMUNICATION_GESTURES, db_index=True)
    communication_telepathic = RelationIntegerField(relation=game_relations.COMMUNICATION_TELEPATHIC, db_index=True)

    intellect_level = RelationIntegerField(relation=game_relations.INTELLECT_LEVEL, db_index=True)

    class Meta:
        permissions = (("create_mobrecord", u"Может предлагать мобов"),
                       ("moderate_mobrecord", u"Может утверждать мобов"),)
