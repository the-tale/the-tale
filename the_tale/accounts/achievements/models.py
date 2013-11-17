# coding: utf-8

from django.db import models

from rels.django_staff import TableIntegerField

from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE


class Achievement(models.Model):

    CAPTION_MAX_LENGTH = 128
    DESCRIPTION_MAX_LENGTH = 1024

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    group = TableIntegerField(relation=ACHIEVEMENT_GROUP, db_index=True)
    type = TableIntegerField(relation=ACHIEVEMENT_TYPE, db_index=True)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)

    order = models.IntegerField()

    approved = models.BooleanField(default=False)

    barrier = models.IntegerField()

    points = models.IntegerField()

    class Meta:
        permissions = (('edit_achievement', u'Может создавать и редактировать достижения'),)



class AccountAchievements(models.Model):

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, unique=True)

    achievements = models.TextField(default='{}')

    points = models.IntegerField(default=0)



class GiveAchievementTask(models.Model):
    account = models.ForeignKey('accounts.Account', null=True, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
