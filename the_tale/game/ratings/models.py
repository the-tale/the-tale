# coding: utf-8

from django.db import models


class RatingValues(models.Model):

    account = models.ForeignKey('accounts.Account', null=False)

    might = models.FloatField(default=0, db_index=True)

    bills_count = models.IntegerField(default=0, db_index=True)

    power = models.IntegerField(default=0, db_index=True)

    level = models.IntegerField(default=0, db_index=True)


class RatingPlaces(models.Model):

    account = models.ForeignKey('accounts.Account', null=False)

    might_place = models.BigIntegerField(db_index=True)

    bills_count_place = models.BigIntegerField(db_index=True)

    power_place = models.BigIntegerField(db_index=True)

    level_place = models.BigIntegerField(db_index=True)
