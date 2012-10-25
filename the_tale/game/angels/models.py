from django.db import models

from accounts.models import Account

class Angel(models.Model):

     account = models.OneToOneField(Account, unique=True, null=False)

     energy = models.FloatField(null=False, default=0.0)

     abilities = models.TextField(null=False, default='{}')

     def __unicode__(self):
          return self.account.nick

     @classmethod
     def get_related_query(cls):
          return cls.objects.all()
