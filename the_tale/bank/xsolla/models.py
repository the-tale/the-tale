# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.bank.xsolla.relations import INVOICE_STATE, PAY_RESULT


class Invoice(models.Model):

    XSOLLA_ID_MAX_LENGTH = 255
    XSOLLA_V1_MAX_LENGTH = 255
    XSOLLA_V2_MAX_LENGTH = 200
    XSOLLA_V3_MAX_LENGTH = 100
    COMMENT_MAX_LENGTH = 255
    REQUEST_URL_LENGTH = 1024

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    state = RelationIntegerField(null=True, relation=INVOICE_STATE, relation_column='value', db_index=True)

    bank_id = models.BigIntegerField()
    bank_amount = models.BigIntegerField()
    bank_invoice = models.ForeignKey('bank.Invoice', null=True, unique=True, related_name='+', on_delete=models.SET_NULL) # settuped when payments deposited to account

    xsolla_id = models.CharField(max_length=XSOLLA_ID_MAX_LENGTH, db_index=True)

    xsolla_v1 = models.CharField(max_length=XSOLLA_V1_MAX_LENGTH)
    xsolla_v2 = models.CharField(max_length=XSOLLA_V2_MAX_LENGTH, null=True)
    xsolla_v3 = models.CharField(max_length=XSOLLA_V3_MAX_LENGTH, null=True)

    comment = models.CharField(max_length=COMMENT_MAX_LENGTH, null=False, default=u'')

    pay_result = RelationIntegerField(null=True, relation=PAY_RESULT, relation_column='value', db_index=True)

    test = models.BooleanField(blank=True, default=False)

    date = models.DateTimeField(null=True)

    request_url = models.CharField(max_length=REQUEST_URL_LENGTH)

    class Meta:
        unique_together = (('xsolla_id', 'test'), )
