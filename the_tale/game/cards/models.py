from django.db import models

from game.angels.models import Angel

class Card(models.Model):

     angel = models.ForeignKey(Angel, related_name='cards')
     
     type = models.CharField(max_length=150, null=False)

     cooldown_end = models.IntegerField(default=0, null=False)


class CardsQueueItem(models.Model):

     created_at = models.DateTimeField(auto_now_add=True)

     turn = models.ForeignKey('turns.Turn', null=False)

     card = models.ForeignKey(Card, null=False)

     processed = models.BooleanField(null=False, default=False)

     data = models.TextField(default=u'{}')
