# coding: utf-8
from django.db import models

UNINITIALIZED_STATE = 'uninitialized'


class MetaAction(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    percents = models.FloatField(default=0.0, null=False)

    state = models.CharField(max_length=50, null=False, default=UNINITIALIZED_STATE)

    data = models.TextField(null=False, default='{}')

    bundle = models.ForeignKey('game.Bundle', null=True)


class MetaActionMember(models.Model):

    hero = models.ForeignKey('heroes.Hero', related_name='+')

    action = models.ForeignKey(MetaAction, related_name='+')

    context = models.TextField(null=False, default='{}')

    role = models.CharField(null=False, max_length=32)
