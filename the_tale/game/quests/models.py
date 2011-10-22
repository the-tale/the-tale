from django.db import models

class Quest(models.Model):

    #DO NOT USE THIS FIELD!!!! ONLY USE FOR GET QUESTS INFO FOR HERO
    hero = models.ForeignKey('heroes.Hero', related_name='+', null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    cmd_number = models.IntegerField(null=False, default=0)

    data = models.TextField(null=False, default='{}')
    env = models.TextField(null=False, default='{}')
