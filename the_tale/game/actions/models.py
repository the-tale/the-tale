# coding: utf-8
from django.db import models

UNINITIALIZED_STATE = 'uninitialized'

class Action(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    hero = models.ForeignKey('heroes.Hero', related_name='actions')

    order = models.IntegerField()

    percents = models.FloatField(default=0.0, null=False)

    state = models.CharField(max_length=50, null=False, default=UNINITIALIZED_STATE)

    leader = models.BooleanField(null=False, default=True) #since we create only LEAD actions, leader option MUST be TRUE by default

    parent = models.ForeignKey('self', related_name='+', null=True, blank=True)

    context = models.TextField(null=False, default='{}')

    # action specific fields
    quest = models.ForeignKey('quests.Quest', related_name='+', null=True, blank=True)
    place = models.ForeignKey('places.Place', related_name='+', null=True, blank=True)
    road = models.ForeignKey('roads.Road', related_name='+', null=True, blank=True)
    mob = models.TextField(null=False, default='{}')
    data = models.TextField(null=False, default='{}')
    break_at = models.FloatField(null=True, blank=True, default=None)
    length = models.FloatField(null=True, blank=True, default=None)
    destination_x = models.IntegerField(null=True, blank=True, default=None)
    destination_y = models.IntegerField(null=True, blank=True, default=None)
    percents_barier = models.IntegerField(null=True, blank=True, default=None)
    mob_context = models.TextField(null=False, default='{}')

    @classmethod
    def get_related_query(cls):
        return cls.objects.select_related('hero', 'hero__pos_place', 'hero__pos_road', 'quest', 'place', 'road', 'npc')

    def __unicode__(self):
        return '%s(%d, %s)' % (self.type, self.id, self.state)
