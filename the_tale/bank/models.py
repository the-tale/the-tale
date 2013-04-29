# coding: utf-8

from django.db import models

from rels.django_staff import TableIntegerField

from bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE


class Account(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    entity_type = TableIntegerField(relation=ENTITY_TYPE, relation_column='value', db_index=True)
    entity_id = models.BigIntegerField()

    currency = TableIntegerField(relation=CURRENCY_TYPE, relation_column='value', db_index=True)
    amount = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ( ('entity_id', 'entity_type', 'currency'), )


class Invoice(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    recipient_type = TableIntegerField(relation=ENTITY_TYPE, relation_column='value', db_index=True)
    recipient_id = models.BigIntegerField()

    sender_type = TableIntegerField(relation=ENTITY_TYPE, relation_column='value', db_index=True)
    sender_id = models.BigIntegerField()

    state = TableIntegerField(relation=INVOICE_STATE, relation_column='value', db_index=True)

    currency = TableIntegerField(relation=CURRENCY_TYPE, relation_column='value', db_index=True)
    amount = models.BigIntegerField()

    class Meta:
        index_together = ( ('recipient_type', 'recipient_id', 'currency'),
                           ('sender_type', 'sender_id', 'currency') )
