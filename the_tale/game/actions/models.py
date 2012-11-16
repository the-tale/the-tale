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

    parent = models.ForeignKey('self', related_name='+', null=True, blank=True)

    context = models.TextField(null=False, default='{}')

    # action specific fields
    quest = models.ForeignKey('quests.Quest', related_name='+', null=True, blank=True)
    place = models.ForeignKey('places.Place', related_name='+', null=True, blank=True)
    mob = models.TextField(null=False, default='{}')
    data = models.TextField(null=False, default='{}')
    break_at = models.FloatField(null=True, blank=True, default=None)
    length = models.FloatField(null=True, blank=True, default=None)
    destination_x = models.IntegerField(null=True, blank=True, default=None)
    destination_y = models.IntegerField(null=True, blank=True, default=None)
    percents_barier = models.IntegerField(null=True, blank=True, default=None)
    extra_probability = models.FloatField(null=True, blank=True, default=None)
    mob_context = models.TextField(null=False, default='{}')
    textgen_id = models.CharField(max_length=128, null=True, blank=True, default=None)
    back = models.BooleanField(null=False, default=False)

    meta_action = models.ForeignKey('actions.MetaAction', null=True, default=None)

    def __unicode__(self):
        return '%s(%d, %s)' % (self.type, self.id, self.state)



class MetaAction(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    percents = models.FloatField(default=0.0, null=False)

    state = models.CharField(max_length=50, null=False, default=UNINITIALIZED_STATE)

    data = models.TextField(null=False, default='{}')


class MetaActionMember(models.Model):

    hero = models.ForeignKey('heroes.Hero', related_name='+')

    action = models.ForeignKey(MetaAction, related_name='+')

    context = models.TextField(null=False, default='{}')

    role = models.CharField(null=False, max_length=32)
