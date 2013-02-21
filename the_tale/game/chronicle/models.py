# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

RECORD_TYPE = create_enum('RECORD_TYPE', (('PLACE_CHANGE_NAME_BILL_STARTED', 0, u''),
                                          ('PLACE_CHANGE_NAME_BILL_SUCCESSED', 1, u''),
                                          ('PLACE_CHANGE_NAME_BILL_FAILED', 2, u''),

                                          ('PLACE_CHANGE_DESCRIPTION_BILL_STARTED', 3, u''),
                                          ('PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED', 4, u''),
                                          ('PLACE_CHANGE_DESCRIPTION_BILL_FAILED', 5, u''),

                                          ('PLACE_CHANGE_MODIFIER_BILL_STARTED', 6, u''),
                                          ('PLACE_CHANGE_MODIFIER_BILL_SUCCESSED', 7, u''),
                                          ('PLACE_CHANGE_MODIFIER_BILL_FAILED', 8, u''),
                                          ('PLACE_LOSED_MODIFIER', 9, u''),

                                          ('PERSON_REMOVE_BILL_STARTED', 10, u''),
                                          ('PERSON_REMOVE_BILL_SUCCESSED', 11, u''),
                                          ('PERSON_REMOVE_BILL_FAILED', 12, u''),
                                          ('PERSON_LEFT_PLACE', 13, u''),
                                          ('PERSON_ARRIVED_TO_PLACE', 14, u''),

                                          ('PLACE_CHANGE_RACE', 15, u'') ))


class Record(models.Model):

    type = models.IntegerField(null=False, choices=RECORD_TYPE._CHOICES, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = models.IntegerField(null=False)

    text = models.TextField(null=False, blank=True)
