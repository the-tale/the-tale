
import smart_imports

smart_imports.all()


class Account(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    entity_type = rels_django.RelationIntegerField(relation=relations.ENTITY_TYPE, relation_column='value', db_index=True)
    entity_id = django_models.BigIntegerField()

    currency = rels_django.RelationIntegerField(relation=relations.CURRENCY_TYPE, relation_column='value', db_index=True)
    amount = django_models.BigIntegerField(default=0)

    class Meta:
        unique_together = (('entity_id', 'entity_type', 'currency'), )


class Invoice(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = django_models.DateTimeField(auto_now=True, null=False, db_index=True)

    recipient_type = rels_django.RelationIntegerField(relation=relations.ENTITY_TYPE, relation_column='value', db_index=True)
    recipient_id = django_models.BigIntegerField(db_index=True)

    sender_type = rels_django.RelationIntegerField(relation=relations.ENTITY_TYPE, relation_column='value', db_index=True)
    sender_id = django_models.BigIntegerField(db_index=True)

    state = rels_django.RelationIntegerField(relation=relations.INVOICE_STATE, relation_column='value', db_index=True)

    currency = rels_django.RelationIntegerField(relation=relations.CURRENCY_TYPE, relation_column='value', db_index=True)
    amount = django_models.BigIntegerField()

    operation_uid = django_models.CharField(max_length=64, db_index=True)

    description_for_recipient = django_models.TextField()
    description_for_sender = django_models.TextField()

    class Meta:
        index_together = (('recipient_type', 'recipient_id', 'currency'),
                          ('sender_type', 'sender_id', 'currency'))
