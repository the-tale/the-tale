# coding: utf-8

from django.db import models
from django.conf import settings as project_settings

from rels.django import RelationIntegerField

from utg import relations as utg_relations

from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import keys


class Word(models.Model):
    MAX_FORM_LENGTH = 64

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    author = models.ForeignKey(project_settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('linguistics.Word', null=True, unique=True, on_delete=models.SET_NULL)

    normal_form = models.CharField(max_length=MAX_FORM_LENGTH)
    forms = models.TextField()

    state = RelationIntegerField(relation=relations.WORD_STATE, db_index=True)
    type = RelationIntegerField(relation=utg_relations.WORD_TYPE, db_index=True, choices=[(record, record.text) for record in utg_relations.WORD_TYPE.records])

    used_in_ingame_templates = models.IntegerField(default=0)
    used_in_onreview_templates = models.IntegerField(default=0)
    used_in_status = RelationIntegerField(relation=relations.WORD_USED_IN_STATUS, default=2, db_index=True)

    class Meta:
        unique_together = (('normal_form', 'type', 'state'),)
        permissions = (("moderate_word", u"Может модерировать слова"), )



class Template(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    author = models.ForeignKey(project_settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('linguistics.Template', null=True, unique=True, on_delete=models.SET_NULL)

    raw_template = models.TextField(db_index=True)
    data = models.TextField()

    state = RelationIntegerField(relation=relations.TEMPLATE_STATE, db_index=True)
    key = RelationIntegerField(relation=keys.LEXICON_KEY, db_index=True)

    errors_status = RelationIntegerField(relation=relations.TEMPLATE_ERRORS_STATUS, default=0, db_index=True)

    class Meta:
        permissions = (("moderate_template", u"Может модерировать шаблоны фраз"), )


class Contribution(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    account = models.ForeignKey(project_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    type = RelationIntegerField(relation=relations.CONTRIBUTION_TYPE, default=0, db_index=True)

    # if entity_id < 0 it is id of old phrase_candidate entity
    entity_id = models.BigIntegerField(db_index=True)

    class Meta:
        unique_together = (('type', 'account', 'entity_id'),)



class Restriction(models.Model):
    MAX_NAME_LENGTH = 128

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH)

    group = RelationIntegerField(relation=relations.TEMPLATE_RESTRICTION_GROUP, db_index=True)
    external_id = models.BigIntegerField(db_index=True)

    class Meta:
        unique_together = (('group', 'external_id'),)
