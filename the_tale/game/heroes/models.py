from django.db import models

from game.angels.models import Angel
from game.actions.models import Action

class Hero(models.Model):

    angel = models.ForeignKey(Angel, related_name='heroes', default=None, null=True, blank=True)

    npc = models.BooleanField(default=False)
    alive = models.BooleanField(default=True)

    actions = models.ManyToManyField(Action, related_name='heroes', through='HeroAction')

    #base
    first = models.BooleanField()

    name = models.CharField(max_length=150, null=False)

    wisdom = models.IntegerField()

    health = models.FloatField(null=False, default=0.0)

    #primary
    intellect = models.IntegerField()
    constitution = models.IntegerField()
    reflexes = models.IntegerField()
    chaoticity = models.IntegerField()

    #secondary

    #accumulated


class HeroAction(models.Model):
    
    hero = models.ForeignKey(Hero)
    action = models.ForeignKey(Action)

    order = models.IntegerField()
