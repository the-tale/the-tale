
from django.db import models

class Action(models.Model):

    class STATE:
        UNINITIALIZED = 'uninitialized'
        PROCESSED = 'processed'

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    percents = models.FloatField(null=False)

    state = models.CharField(max_length=50, null=False, default=STATE.UNINITIALIZED)

    entropy = models.IntegerField(null=False, default=0)


class ActionIdleness(models.Model):

    class STATE(Action.STATE):
        pass
    
    base_action = models.OneToOneField(Action, related_name='action_idleness')

    hero = models.ForeignKey('heroes.Hero', related_name='+')

    entropy_action = models.ForeignKey(Action, related_name='+', default=None, null=True, on_delete=models.SET_NULL)


class ActionQuestMailDelivery(models.Model):

    class STATE(Action.STATE):
        MOVE_TO_DELIVERY_FROM_POINT = 'move_to_delivery_from_point'
        MOVE_TO_DELIVERY_TO_POINT = 'move_to_delivery_to_point'
    
    base_action = models.OneToOneField(Action, related_name='action_quest')

    quest = models.ForeignKey('quests.Quest', related_name='+', default=None, null=True)

    action_move_to_delivery_from = models.ForeignKey('actions.action', related_name='+', null=True, default=None, on_delete=models.SET_NULL)
    action_move_to_delivery_to = models.ForeignKey('actions.action', related_name='+', null=True, default=None, on_delete=models.SET_NULL)


class ActionMoveTo(models.Model):

    class STATE(Action.STATE):
        MOVING = 'moving'
    
    base_action = models.OneToOneField(Action, related_name='action_move_to')

    hero = models.ForeignKey('heroes.Hero', related_name='+')

    destination = models.ForeignKey('places.Place', related_name='+')

    road = models.ForeignKey('roads.Road', related_name='+', null=True, default=None, on_delete=models.SET_NULL)

    entropy_action = models.ForeignKey(Action, related_name='+', default=None, null=True, on_delete=models.SET_NULL)


class ActionBattlePvE_1x1(models.Model):

    class STATE(Action.STATE):
        BATTLE_RUNNING = 'battle_running'

    base_action = models.OneToOneField(Action, related_name='action_battle_pve_1x1')

    hero = models.ForeignKey('heroes.Hero', related_name='+')
    npc = models.ForeignKey('heroes.Hero', related_name='+')

    hero_initiative = models.FloatField(null=False, default=0.0)
    npc_initiative = models.FloatField(null=False, default=0.0)


class ActionResurrect(models.Model):

    class STATE(Action.STATE):
        RESURRECT = 'resurrect'

    base_action = models.OneToOneField(Action, related_name='action_resurrect')

    hero = models.ForeignKey('heroes.Hero', related_name='+')
    

