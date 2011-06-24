from django.db import models

class Quest(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=150, null=False)

    state = models.CharField(max_length=50)

    percents = models.FloatField(null=False, default=0.0)


class QuestMailDelivery(models.Model):

    base_quest = models.OneToOneField(Quest, related_name='mail_delivery')

    hero = models.ForeignKey('heroes.Hero', related_name='+', null=False)

    delivery_from = models.ForeignKey('places.Place', related_name='quests_mail_delivery_from')
    delivery_to = models.ForeignKey('places.Place', related_name='quests_mail_delivery_to')

