# coding: utf-8

from django.db import models

from rels.django_staff import TableIntegerField

from accounts.clans.relations import MEMBER_ROLE


class Clan(models.Model):

    MAX_NAME_LENGTH = 128
    MAX_ABBR_LENGTH = 5
    MAX_MOTTO_LENGTH = 256
    MAX_DESCRIPTION_LENGTH = 2024

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, db_index=True)
    abbr = models.CharField(max_length=MAX_ABBR_LENGTH, db_index=True)

    motto = models.CharField(max_length=MAX_MOTTO_LENGTH)
    description = models.TextField(max_length=MAX_DESCRIPTION_LENGTH)

    members_number = models.IntegerField()



class ClanMembership(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    clan = models.ForeignKey(Clan)
    account = models.ForeignKey('accounts.Account')

    role = TableIntegerField(relation=MEMBER_ROLE, relation_column='value')
