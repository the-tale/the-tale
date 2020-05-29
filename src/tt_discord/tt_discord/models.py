

from django.db import models

from django.contrib.postgres import fields as postgres_fields


class Account(models.Model):

    id = models.BigAutoField(primary_key=True)

    discord_id = models.BigIntegerField(null=True, unique=True)

    game_id = models.BigIntegerField(null=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'accounts'


class GameData(models.Model):

    account = models.ForeignKey(Account, related_name='+', on_delete=models.CASCADE, db_column='account')

    type = models.IntegerField()

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = 'game_data'
        unique_together = (('account', 'type'),)
        index_together = (('updated_at', 'synced_at'),)


class BindCode(models.Model):

    id = models.BigAutoField(primary_key=True)

    code = models.UUIDField(unique=True)

    account = models.OneToOneField(Account, related_name='+', on_delete=models.CASCADE, db_column='account')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expire_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'bind_codes'
