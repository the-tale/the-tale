# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from utg.relations import WORD_TYPE

from the_tale.linguistics import relations


class Word(models.Model):
    MAX_FORM_LENGTH = 64

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    normal_form = models.CharField(max_length=MAX_FORM_LENGTH)
    forms = models.TextField()

    state = RelationIntegerField(relation=relations.WORD_STATE, db_index=True)
    type = RelationIntegerField(relation=WORD_TYPE, db_index=True)
