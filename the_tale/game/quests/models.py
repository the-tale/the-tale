from django.db import models

class Quest(models.Model):

    class STATE:
        UNINITIALIZED = 'uninitialized'
        COMPLETED = 'completed'

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    state = models.CharField(max_length=50, default=STATE.UNINITIALIZED)

    percents = models.FloatField(null=False, default=0.0)


class QuestMailDelivery(models.Model):

    class STATE(Quest.STATE):
        MOVE_TO_DELIVERY_FROM_POINT = 'move_to_delivery_from_point'
        MOVE_TO_DELIVERY_TO_POINT = 'move_to_delivery_to_point'

    base_quest = models.OneToOneField(Quest, related_name='mail_delivery')

    hero = models.ForeignKey('heroes.Hero', related_name='+', null=False)

    delivery_from = models.ForeignKey('places.Place', related_name='quests_mail_delivery_from')
    delivery_to = models.ForeignKey('places.Place', related_name='quests_mail_delivery_to')

