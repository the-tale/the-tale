# coding: utf-8

import datetime

from django.db import models

from accounts.models import Account

class Angel(models.Model):

     account = models.OneToOneField(Account, unique=True, null=False)

     energy = models.FloatField(null=False, default=0.0)

     abilities = models.TextField(null=False, default='{}')

     might = models.FloatField(null=False, default=0.0)
     might_updated_time = models.DateTimeField(auto_now_add=True, db_index=True, default=datetime.datetime(2000, 1, 1))

     def __unicode__(self):
          return self.account.nick

     @classmethod
     def get_related_query(cls):
          return cls.objects.all()
