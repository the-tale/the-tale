# coding: utf-8
from django.db import models

from rels.django_staff import TableIntegerField

from forum.models import Thread

from game.bills.relations import BILL_STATE, BILL_TYPE, VOTE_TYPE


class Bill(models.Model):

    CAPTION_MIN_LENGTH = 10
    CAPTION_MAX_LENGTH = 256

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False) # MUST setupped by hand

    created_at_turn = models.IntegerField(null=False)

    owner = models.ForeignKey('accounts.Account', null=False, related_name='+')

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    type = TableIntegerField(relation=BILL_TYPE, relation_column='value', db_index=True)
    state = TableIntegerField(relation=BILL_STATE, relation_column='value', db_index=True)

    approved_by_moderator = models.BooleanField(default=False, db_index=True)

    remove_initiator = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+')

    rationale = models.TextField(null=False, blank=True)
    technical_data = models.TextField(null=False, blank=True, default={})
    reject_reason = models.TextField(null=False, blank=True)

    # we should not remove bill when ocasionally remove forum thread
    forum_thread = models.ForeignKey(Thread, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    votes_for = models.IntegerField(default=0)
    votes_against = models.IntegerField(default=0)
    votes_refrained = models.IntegerField(default=0)

    # fields to store config values after processing state (since they can be changed in future)
    min_votes_required = models.IntegerField(default=0)
    min_votes_percents_required = models.FloatField(default=0.0)

    class Meta:
        permissions = (("moderate_bill", u"Может администрировать законопроекты"), )


class Actor(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    bill = models.ForeignKey(Bill, null=False)

    place = models.ForeignKey('places.Place', null=True, related_name='+')


class Vote(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    owner = models.ForeignKey('accounts.Account', null=False, related_name='+')

    bill = models.ForeignKey(Bill, null=False)

    type = TableIntegerField(relation=VOTE_TYPE, relation_column='value', db_index=True)

    class Meta:
        unique_together = (('owner', 'bill'),)
