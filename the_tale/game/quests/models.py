# coding: utf-8
from django.db import models

class Quest(models.Model):

    #DO NOT USE THIS FIELD FROM WORKERS!!!! ONLY USE FOR GET QUESTS INFO FOR HERO
    hero = models.ForeignKey('heroes.Hero', related_name='+', null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    cmd_number = models.IntegerField(null=False, default=0)

    data = models.TextField(null=False, default='{}')
    env = models.TextField(null=False, default='{}')


class QuestChoice(models.Model):

    quest = models.ForeignKey(Quest, related_name='choices')

    choice_point = models.CharField(max_length=32)

    choice = models.CharField(max_length=32)

    class Meta:
        unique_together = ('quest', 'choice_point')
