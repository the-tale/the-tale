# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game.phrase_candidates import relations



class PhraseCandidate(models.Model):

    MAX_TEXT_LENGTH = 1024*10

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    author = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)
    moderator = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    text = models.TextField(null=False, blank=True, max_length=MAX_TEXT_LENGTH)

    type = models.CharField(null=False, blank=False, max_length=256)
    type_name = models.CharField(null=False, blank=False, max_length=256, default=u'')

    subtype = models.CharField(null=False, blank=False, max_length=256, default=u'')
    subtype_name = models.CharField(null=False, blank=False, max_length=256, default=u'')

    state = RelationIntegerField(relation=relations.PHRASE_CANDIDATE_STATE, db_index=True)

    class Meta:
        permissions = (('moderate_phrasecandidate', u'Может редактировать фразы-кандидаты'),  # game designer
                       ('add_to_game_phrasecandidate', u'Может добавлять фразы-кандидаты'), ) # developer
