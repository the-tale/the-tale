
import smart_imports

smart_imports.all()


class RatingValues(django_models.Model):

    account = django_models.ForeignKey('accounts.Account', null=False, on_delete=django_models.CASCADE)

    might = django_models.FloatField(default=0, db_index=True)

    bills_count = django_models.IntegerField(default=0, db_index=True)

    magic_power = django_models.IntegerField(default=0, db_index=True)
    physic_power = django_models.IntegerField(default=0, db_index=True)

    level = django_models.IntegerField(default=0, db_index=True)

    phrases_count = django_models.IntegerField(default=0, db_index=True)

    pvp_battles_1x1_number = django_models.IntegerField(default=0, db_index=True)
    pvp_battles_1x1_victories = django_models.FloatField(default=0.0, db_index=True)

    referrals_number = django_models.IntegerField(default=0, db_index=True)

    achievements_points = django_models.IntegerField(default=0, db_index=True)

    politics_power = django_models.FloatField(default=0, db_index=True)


class RatingPlaces(django_models.Model):

    account = django_models.ForeignKey('accounts.Account', null=False, on_delete=django_models.CASCADE)

    might_place = django_models.BigIntegerField(db_index=True)

    bills_count_place = django_models.BigIntegerField(db_index=True)

    magic_power_place = django_models.BigIntegerField(db_index=True)
    physic_power_place = django_models.BigIntegerField(db_index=True)

    level_place = django_models.BigIntegerField(db_index=True)

    phrases_count_place = django_models.BigIntegerField(db_index=True)

    pvp_battles_1x1_number_place = django_models.BigIntegerField(db_index=True)
    pvp_battles_1x1_victories_place = django_models.BigIntegerField(db_index=True)

    referrals_number_place = django_models.IntegerField(default=0, db_index=True)

    achievements_points_place = django_models.IntegerField(default=0, db_index=True)

    politics_power_place = django_models.IntegerField(default=0, db_index=True)
