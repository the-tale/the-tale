
from django.db import models

class Action(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    hero = models.ForeignKey('heroes.Hero', related_name='+')

    order = models.IntegerField()

    percents = models.FloatField(null=False)

    state = models.CharField(max_length=50, null=False)

    entropy = models.IntegerField(null=False, default=0)

    leader = models.BooleanField(null=False, default=False)

    child_action = models.ForeignKey('self', related_name='+', null=True, on_delete=models.SET_NULL)

    # action specific fields
    quest = models.ForeignKey('quests.Quest', related_name='+', null=True)
    place = models.ForeignKey('places.Place', related_name='+', null=True)
    road = models.ForeignKey('roads.Road', related_name='+', null=True)
    npc = models.ForeignKey('heroes.Hero', related_name='+')
    data = models.TextField(null=False, default='{}')
