from django.db import models

class Quest(models.Model):

    hero = models.ForeignKey('heroes.Hero', related_name='+', null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    percents = models.FloatField(null=False, default=0.0)

    story = models.TextField(null=False, default='[]')
    data = models.TextField(null=False, default='{}')
    env = models.TextField(null=False, default='{}')
