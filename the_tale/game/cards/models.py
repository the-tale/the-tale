from django.db import models

from game.angels.models import Angel

class Card(models.Model):

     angel = models.ForeignKey(Angel, related_name='cards')
     
     type = models.CharField(max_length=150, null=False)

     cooldown_end = models.IntegerField(default=0, null=False)
