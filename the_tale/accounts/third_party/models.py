# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.common.utils.models import UUIDField

from the_tale.accounts.third_party import relations


class AccessToken(models.Model):
    APPLICATION_NAME_MAX_LENGTH = 100
    APPLICATION_INFO_MAX_LENGTH = 100


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    account = models.ForeignKey('accounts.Account', null=True, default=None, on_delete=models.CASCADE)

    uid = UUIDField(unique=True, db_index=True)

    application_name = models.CharField(max_length=APPLICATION_NAME_MAX_LENGTH)

    application_info = models.CharField(max_length=APPLICATION_INFO_MAX_LENGTH)

    application_description = models.TextField()

    state = RelationIntegerField(relation=relations.ACCESS_TOKEN_STATE)
