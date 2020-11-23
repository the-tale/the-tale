

from django.db import models

from django.contrib.postgres import fields as postgres_fields


class AccountInfo(models.Model):

    id = models.BigIntegerField(primary_key=True)

    state = models.IntegerField()

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_infos'


class Token(models.Model):
    id = models.BigAutoField(primary_key=True)

    account = models.OneToOneField(AccountInfo, related_name='+', on_delete=models.CASCADE, db_column='account')

    value = models.TextField()

    expire_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tokens'


class Invoice(models.Model):

    id = models.BigAutoField(primary_key=True)

    xsolla_id = models.BigIntegerField(unique=True, null=True)

    account = models.ForeignKey(AccountInfo, related_name='+', on_delete=models.PROTECT, db_column='account')

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_test = models.BooleanField()
    is_fake = models.BooleanField()

    processed_at = models.DateTimeField(null=True, default=None, db_index=True)

    class Meta:
        db_table = 'invoices'


class Cancellation(models.Model):

    id = models.BigAutoField(primary_key=True)

    account = models.ForeignKey(AccountInfo, related_name='+', on_delete=models.PROTECT, db_column='account')

    xsolla_id = models.BigIntegerField(unique=True)

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    processed_at = models.DateTimeField(null=True, default=None)

    class Meta:
        db_table = 'cancellations'
