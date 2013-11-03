# coding: utf-8
from django.db import models

from rels.django_staff import TableIntegerField

from the_tale.forum.models import Thread

from the_tale.game.bills.relations import BILL_STATE, BILL_TYPE, VOTE_TYPE, BILL_DURATION


class Bill(models.Model):

    CAPTION_MIN_LENGTH = 10
    CAPTION_MAX_LENGTH = 256

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False) # MUST setupped by hand
    voting_end_at = models.DateTimeField(null=True)

    created_at_turn = models.IntegerField(null=False)

    ends_at_turn = models.BigIntegerField(null=True, blank=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = TableIntegerField(relation=BILL_DURATION, relation_column='value')

    owner = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    type = TableIntegerField(relation=BILL_TYPE, relation_column='value', db_index=True)
    state = TableIntegerField(relation=BILL_STATE, relation_column='value', db_index=True)

    approved_by_moderator = models.BooleanField(default=False, db_index=True)

    remove_initiator = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    rationale = models.TextField(null=False, blank=True)
    technical_data = models.TextField(null=False, blank=True, default={})
    reject_reason = models.TextField(null=False, blank=True)

    # we should not remove bill when ocasionally remove forum thread
    forum_thread = models.ForeignKey(Thread, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    votes_for = models.IntegerField(default=0)
    votes_against = models.IntegerField(default=0)
    votes_refrained = models.IntegerField(default=0)

    # fields to store config values after processing state (since they can be changed in future)
    min_votes_percents_required = models.FloatField(default=0.0)

    is_declined = models.BooleanField(blank=True, default=False)
    declined_by = models.ForeignKey('bills.Bill', null=True, default=None, related_name='+', blank=True, on_delete=models.SET_NULL)

    class Meta:
        permissions = (("moderate_bill", u"Может администрировать законопроекты"), )


class Actor(models.Model):
    # ATTENTION: if you want to make building an actor, remember, that after it recreated
    # (for same person after destroying previouse building)
    # it first fully removed from base (previouse building) and only then created

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    bill = models.ForeignKey(Bill, null=False, on_delete=models.CASCADE)

    place = models.ForeignKey('places.Place', null=True, related_name='+', on_delete=models.CASCADE)


class Vote(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    owner = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)

    bill = models.ForeignKey(Bill, null=False, on_delete=models.CASCADE)

    type = TableIntegerField(relation=VOTE_TYPE, relation_column='value', db_index=True)

    class Meta:
        unique_together = (('owner', 'bill'),)
