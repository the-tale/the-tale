# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE


class Account(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    entity_type = RelationIntegerField(relation=ENTITY_TYPE, relation_column='value', db_index=True)
    entity_id = models.BigIntegerField()

    currency = RelationIntegerField(relation=CURRENCY_TYPE, relation_column='value', db_index=True)
    amount = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ( ('entity_id', 'entity_type', 'currency'), )


class Invoice(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, null=False, db_index=True)

    recipient_type = RelationIntegerField(relation=ENTITY_TYPE, relation_column='value', db_index=True)
    recipient_id = models.BigIntegerField(db_index=True)

    sender_type = RelationIntegerField(relation=ENTITY_TYPE, relation_column='value', db_index=True)
    sender_id = models.BigIntegerField(db_index=True)

    state = RelationIntegerField(relation=INVOICE_STATE, relation_column='value', db_index=True)

    currency = RelationIntegerField(relation=CURRENCY_TYPE, relation_column='value', db_index=True)
    amount = models.BigIntegerField()

    operation_uid = models.CharField(max_length=64, db_index=True)

    description_for_recipient = models.TextField()
    description_for_sender = models.TextField()

    class Meta:
        index_together = ( ('recipient_type', 'recipient_id', 'currency'),
                           ('sender_type', 'sender_id', 'currency') )
