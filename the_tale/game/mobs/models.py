# coding: utf-8

from django.db import models

from rels.django import TableIntegerField

from the_tale.game.mobs.relations import MOB_RECORD_STATE, MOB_TYPE


class MobRecord(models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    editor = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    state = TableIntegerField(relation=MOB_RECORD_STATE, relation_column='value')
    type = TableIntegerField(relation=MOB_TYPE, relation_column='value')

    level = models.IntegerField(default=0)

    uuid = models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    name_forms = models.TextField(null=False)

    description = models.TextField(null=False, default=u'')

    abilities = models.TextField(null=False)

    terrains = models.TextField(null=False)

    class Meta:
        permissions = (("create_mobrecord", u"Может предлагать мобов"),
                       ("moderate_mobrecord", u"Может утверждать мобов"),)
