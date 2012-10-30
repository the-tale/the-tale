# coding: utf-8

from django.db import models


class BUNDLE_TYPE:
    BASIC = 0

BUNDLE_TYPE_CHOICES = ( (BUNDLE_TYPE.BASIC, u'базовый'), )


class Bundle(models.Model):

    type =  models.IntegerField(null=False, choices=BUNDLE_TYPE_CHOICES)

    owner = models.CharField(null=True, max_length=32)


class BundleMember(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, related_name='+', unique=True)
    bundle = models.ForeignKey(Bundle, null=False, related_name='members')
