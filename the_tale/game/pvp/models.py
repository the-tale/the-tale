# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game.pvp.relations import BATTLE_1X1_STATE, BATTLE_1X1_RESULT

class Battle1x1(models.Model):

    account = models.OneToOneField('accounts.Account', null=False, related_name='+', on_delete=models.PROTECT)
    enemy = models.OneToOneField('accounts.Account', null=True, related_name='+', on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    state = RelationIntegerField(relation=BATTLE_1X1_STATE, relation_column='value', db_index=True)

    calculate_rating = models.BooleanField(default=False, db_index=True)


class Battle1x1Result(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    participant_1 = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)
    participant_2 = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)

    result = RelationIntegerField(relation=BATTLE_1X1_RESULT, relation_column='value', db_index=True)
