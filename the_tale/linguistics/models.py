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

    parent = models.ForeignKey('linguistics.Word', null=True, on_delete=models.SET_NULL)

    normal_form = models.CharField(max_length=MAX_FORM_LENGTH)
    forms = models.TextField()

    state = RelationIntegerField(relation=relations.WORD_STATE, db_index=True)
    type = RelationIntegerField(relation=utg_relations.WORD_TYPE, db_index=True, choices=[(record, record.text) for record in utg_relations.WORD_TYPE.records])

    class Meta:
        unique_together = (('normal_form', 'type', 'state'),)
        permissions = (("moderate_word", u"Может модерировать слова"), )



class Template(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    author = models.ForeignKey(project_settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('linguistics.Template', null=True, on_delete=models.SET_NULL)

    raw_template = models.TextField()
    data = models.TextField()

    state = RelationIntegerField(relation=relations.TEMPLATE_STATE, db_index=True)
    key = RelationIntegerField(relation=keys.LEXICON_KEY, db_index=True)

    class Meta:
        permissions = (("moderate_template", u"Может модерировать шаблоны фраз"), )
