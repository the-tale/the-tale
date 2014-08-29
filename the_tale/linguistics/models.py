# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from utg import relations as utg_relations

from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import keys


class Word(models.Model):
    MAX_FORM_LENGTH = 64

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    normal_form = models.CharField(max_length=MAX_FORM_LENGTH)
    forms = models.TextField()

    state = RelationIntegerField(relation=relations.WORD_STATE, db_index=True)
    type = RelationIntegerField(relation=utg_relations.WORD_TYPE, db_index=True)

    class Meta:
        unique_together = (('normal_form', 'type', 'state'),)



class Template(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    template = models.TextField()
    data = models.TextField()

    state = RelationIntegerField(relation=relations.TEMPLATE_STATE, db_index=True)
    key = RelationIntegerField(relation=keys.LEXICON_KEY, db_index=True)

    class Meta:
        unique_together = (('template', 'key', 'state'),)
