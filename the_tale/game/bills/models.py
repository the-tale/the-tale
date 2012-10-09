# coding: utf-8
import datetime

from django.db import models

from django.contrib.auth.models import User

from common.utils.enum import create_enum

from forum.models import Thread

BILL_STATE = create_enum('BILL_STATE', (('VOTING', 1, u'на голосовании'),
                                        ('ACCEPTED', 2, u'принят'),
                                        ('REJECTED', 3, u'отклонён'), ))

BILL_REJECTED_REASONS = create_enum('BILL_REJECTED_REASONS', (('BLOCKED_BY_MODERATOR', 0, u'заблокировано модератором'),
                                                              ('PROPOSAL_TIMEOUT', 1, u'истекло время выдвижения'),
                                                              ('VOTING_FAILED', 2, u'не прошло голосование'), ) )

BILL_TYPE = create_enum('BILL_TYPE', (('PLACE_RENAMING', 0, u'переименование места'),))



class Bill(models.Model):

    CAPTION_MIN_LENGTH = 10
    CAPTION_MAX_LENGTH = 256

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))
    step_started_at = models.DateTimeField(auto_now_add=True, null=False)

    created_at_turn = models.IntegerField(null=False)

    owner = models.ForeignKey(User, null=False, related_name='+')

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    type = models.IntegerField(null=False, choices=BILL_TYPE.CHOICES, db_index=True)
    state = models.IntegerField(null=False, default=BILL_STATE.VOTING, choices=BILL_STATE.CHOICES, db_index=True)
    rejected_state = models.IntegerField(null=True, default=None, choices=BILL_REJECTED_REASONS.CHOICES)

    approved_by_moderator = models.BooleanField(default=False, db_index=True)

    rationale = models.TextField(null=False, blank=True)
    technical_data = models.TextField(null=False, blank=True, default={})
    reject_reason = models.TextField(null=False, blank=True)

    forum_thread = models.ForeignKey(Thread, null=False, blank=True, related_name='+')

    votes_for = models.IntegerField(default=0)
    votes_against = models.IntegerField(default=0)

    # fields to store config values after processing state (since they can be changed in future)
    min_votes_required = models.IntegerField(default=0)
    min_votes_percents_required = models.FloatField(default=0.0)


class Vote(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    owner = models.ForeignKey(User, null=False, related_name='+')

    bill = models.ForeignKey(Bill, null=False, related_name='+')

    value = models.BooleanField(null=False, db_index=True)
