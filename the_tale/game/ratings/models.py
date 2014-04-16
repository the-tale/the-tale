# coding: utf-8

from django.db import models


class RatingValues(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, on_delete=models.CASCADE)

    might = models.FloatField(default=0, db_index=True)

    bills_count = models.IntegerField(default=0, db_index=True)

    magic_power = models.IntegerField(default=0, db_index=True)
    physic_power = models.IntegerField(default=0, db_index=True)

    level = models.IntegerField(default=0, db_index=True)

    phrases_count = models.IntegerField(default=0, db_index=True)

    pvp_battles_1x1_number = models.IntegerField(default=0, db_index=True)
    pvp_battles_1x1_victories = models.FloatField(default=0.0, db_index=True)

    referrals_number = models.IntegerField(default=0, db_index=True)

    achievements_points = models.IntegerField(default=0, db_index=True)

    help_count = models.IntegerField(default=0, db_index=True)


class RatingPlaces(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, on_delete=models.CASCADE)

    might_place = models.BigIntegerField(db_index=True)

    bills_count_place = models.BigIntegerField(db_index=True)

    magic_power_place = models.BigIntegerField(db_index=True)
    physic_power_place = models.BigIntegerField(db_index=True)

    level_place = models.BigIntegerField(db_index=True)

    phrases_count_place = models.BigIntegerField(db_index=True)

    pvp_battles_1x1_number_place = models.BigIntegerField(db_index=True)
    pvp_battles_1x1_victories_place = models.BigIntegerField(db_index=True)

    referrals_number_place = models.IntegerField(default=0, db_index=True)

    achievements_points_place = models.IntegerField(default=0, db_index=True)

    help_count_place = models.IntegerField(default=0, db_index=True)
