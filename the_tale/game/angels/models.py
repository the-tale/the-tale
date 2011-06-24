from django.db import models

from accounts.models import Account

class Angel(models.Model):

     account = models.OneToOneField(Account, unique=True, null=False)
     
     name = models.CharField(max_length=150, unique=True, null=False)
