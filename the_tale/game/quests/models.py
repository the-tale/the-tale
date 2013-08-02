# coding: utf-8
from django.db import models

class Quest(models.Model):

    heroes = models.ManyToManyField('heroes.Hero', through='QuestsHeroes')

    created_at = models.DateTimeField(auto_now_add=True)

    created_at_turn = models.BigIntegerField(null=False, default=0)

    data = models.TextField(null=False, default='{}')
    env = models.TextField(null=False, default='{}')

    def __unicode__(self): return u'%d' % self.id


class QuestsHeroes(models.Model):
    hero = models.ForeignKey('heroes.Hero', related_name='+', null=False, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, related_name='+', null=False, on_delete=models.CASCADE)


class QuestChoice(models.Model):

    quest = models.ForeignKey(Quest, related_name='choices', on_delete=models.CASCADE)

    choice_point = models.CharField(max_length=32)

    choice = models.CharField(max_length=32)

    class Meta:
        unique_together = ('quest', 'choice_point')
