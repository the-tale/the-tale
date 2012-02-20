# coding: utf-8

from django.db import models

class Phrase(models.Model):

    type = models.CharField(null=False, max_length=64, db_index=True)
    
    template = models.TextField(null=False, default='')
