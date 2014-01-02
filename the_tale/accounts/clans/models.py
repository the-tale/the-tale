# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.accounts.clans.relations import MEMBER_ROLE, MEMBERSHIP_REQUEST_TYPE


class Clan(models.Model):

    MAX_NAME_LENGTH = 128
    MIN_NAME_LENGTH = 5
    MAX_ABBR_LENGTH = 5
    MIN_ABBR_LENGTH = 2
    MAX_MOTTO_LENGTH = 256
    MAX_DESCRIPTION_LENGTH = 2024

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    abbr = models.CharField(max_length=MAX_ABBR_LENGTH, unique=True)

    motto = models.CharField(max_length=MAX_MOTTO_LENGTH)
    description = models.TextField(max_length=MAX_DESCRIPTION_LENGTH)

    members_number = models.IntegerField()

    forum_subcategory = models.ForeignKey('forum.SubCategory', on_delete=models.PROTECT)

    def __unicode__(self): return u'[%s] %s' % (self.abbr, self.name)


class Membership(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    clan = models.ForeignKey(Clan, on_delete=models.PROTECT)
    account = models.ForeignKey('accounts.Account', unique=True, on_delete=models.PROTECT)

    role = RelationIntegerField(relation=MEMBER_ROLE, relation_column='value')


class MembershipRequest(models.Model):

    MAX_TEXT_LENGTH = 1024

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.Account', related_name='+', on_delete=models.CASCADE)

    initiator = models.ForeignKey('accounts.Account', related_name='+', on_delete=models.CASCADE)

    type = RelationIntegerField(relation=MEMBERSHIP_REQUEST_TYPE, relation_column='value')

    text = models.TextField(max_length=MAX_TEXT_LENGTH)

    class Meta:
        unique_together = (('clan', 'account'), )
