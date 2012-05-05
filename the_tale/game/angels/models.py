from django.db import models

from accounts.models import Account

class Angel(models.Model):

     account = models.OneToOneField(Account, unique=True, null=False)

     name = models.CharField(max_length=150, unique=True, null=False)

     energy = models.FloatField(null=False, default=0.0)

     abilities = models.TextField(null=False, default='{}')

     updated_at_turn = models.BigIntegerField(null=False, default=0)

     def __unicode__(self):
          return self.name

     @classmethod
     def get_related_query(cls):
          return cls.objects.all() #select_related('pos_place', 'pos_road')
