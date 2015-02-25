# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.market import relations



class Lot(models.Model):

    TYPE_MAX_LENGTH = 16
    UID_MAX_LENGTH = 64
    NAME_MAX_LENGTH = 128

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    type = models.CharField(max_length=TYPE_MAX_LENGTH, db_index=True)
    good_uid = models.CharField(max_length=UID_MAX_LENGTH, db_index=True)

    name = models.CharField(max_length=NAME_MAX_LENGTH, db_index=True)

    seller = models.ForeignKey('accounts.Account', related_name='+', on_delete=models.CASCADE)
    buyer = models.ForeignKey('accounts.Account', default=None, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)

    state = RelationIntegerField(relation=relations.LOT_STATE, db_index=True)

    price = models.IntegerField()

    data = models.TextField(default='{}')

    class Meta:
        get_latest_by = 'created_at'
        unique_together = ( ('seller', 'good_uid'), )



class Goods(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)

    data = models.TextField(default='{}')
