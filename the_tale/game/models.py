# coding: utf-8

from django.db import models


class BUNDLE_TYPE:
    BASIC = 0

BUNDLE_TYPE_CHOICES = ( (BUNDLE_TYPE.BASIC, u'базовый'), ) 


class Bundle(models.Model):

    type =  models.IntegerField(null=False, choices=BUNDLE_TYPE_CHOICES)

    owner = models.CharField(null=True, max_length=32)

    members = models.ManyToManyField('game.BundleMember')


class BundleMember(models.Model):

    angel = models.ForeignKey('angels.Angel', null=True, related_name='bundle')
