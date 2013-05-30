# coding: utf-8

from django.db import models

from rels.django_staff import TableIntegerField

from accounts.models import Account

from bank.relations import ENTITY_TYPE as BANK_ENTITY_TYPE, CURRENCY_TYPE as BANK_CURRENCY_TYPE

from bank.dengionline.relations import CURRENCY_TYPE, INVOICE_STATE


class Invoice(models.Model):

    MAX_COMMENT_LENGTH = 500 / 4 # dengionline expect 500 characters in url, so we restrict them to 500/4 unicode characters

    AMOUNT_DIGITS_AFTER_DOT = 2
    AMOUNT_DIGITS_BEFORE_DOT = 10
    AMOUNT_DIGITS = AMOUNT_DIGITS_BEFORE_DOT + AMOUNT_DIGITS_AFTER_DOT

    MAX_PAYMENT_ID_LENGTH = 30 # 30
    MAX_SERVER_ID_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    state = TableIntegerField(null=True, relation=INVOICE_STATE, relation_column='value', db_index=True) # defoult RUB

    bank_type = TableIntegerField(relation=BANK_ENTITY_TYPE, relation_column='value', db_index=True)
    bank_id = models.BigIntegerField()
    bank_currency = TableIntegerField(relation=BANK_CURRENCY_TYPE, relation_column='value', db_index=True)
    bank_amount = models.BigIntegerField()

    user_id = models.EmailField(max_length=Account.MAX_EMAIL_LENGTH, null=False, db_index=True) # windows-1251
    comment = models.CharField(max_length=MAX_COMMENT_LENGTH, null=False)

    payment_amount = models.DecimalField(decimal_places=AMOUNT_DIGITS_AFTER_DOT, max_digits=AMOUNT_DIGITS) # разделитель - точка
    payment_currency = TableIntegerField(relation=CURRENCY_TYPE, relation_column='value', db_index=True)

    received_amount = models.DecimalField(null=True, decimal_places=AMOUNT_DIGITS_AFTER_DOT, max_digits=AMOUNT_DIGITS) # разделитель - точка
    received_currency = TableIntegerField(null=True, relation=CURRENCY_TYPE, relation_column='value', db_index=True) # defoult RUB

    paymode = models.BigIntegerField(null=True) # int(10)
    payment_id = models.CharField(null=True, max_length=MAX_PAYMENT_ID_LENGTH, unique=True, db_index=True) # int(30)
