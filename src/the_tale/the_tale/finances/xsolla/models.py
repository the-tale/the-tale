
import smart_imports

smart_imports.all()


class Invoice(django_models.Model):

    XSOLLA_ID_MAX_LENGTH = 255
    XSOLLA_V1_MAX_LENGTH = 255
    XSOLLA_V2_MAX_LENGTH = 200
    XSOLLA_V3_MAX_LENGTH = 100
    COMMENT_MAX_LENGTH = 255
    REQUEST_URL_LENGTH = 1024

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    state = rels_django.RelationIntegerField(null=True, relation=relations.INVOICE_STATE, relation_column='value', db_index=True)

    bank_id = django_models.BigIntegerField()
    bank_amount = django_models.BigIntegerField()
    bank_invoice = django_models.OneToOneField('bank.Invoice', null=True, related_name='+', on_delete=django_models.SET_NULL)  # settuped when payments deposited to account

    xsolla_id = django_models.CharField(max_length=XSOLLA_ID_MAX_LENGTH, db_index=True)

    xsolla_v1 = django_models.CharField(max_length=XSOLLA_V1_MAX_LENGTH)
    xsolla_v2 = django_models.CharField(max_length=XSOLLA_V2_MAX_LENGTH, null=True)
    xsolla_v3 = django_models.CharField(max_length=XSOLLA_V3_MAX_LENGTH, null=True)

    comment = django_models.CharField(max_length=COMMENT_MAX_LENGTH, null=False, default='')

    pay_result = rels_django.RelationIntegerField(null=True, relation=relations.PAY_RESULT, relation_column='value', db_index=True)

    test = django_models.BooleanField(blank=True, default=False)

    date = django_models.DateTimeField(null=True)

    request_url = django_models.CharField(max_length=REQUEST_URL_LENGTH)

    class Meta:
        unique_together = (('xsolla_id', 'test'), )
