# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RatingPlaces',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('might_place', models.BigIntegerField(db_index=True)),
                ('bills_count_place', models.BigIntegerField(db_index=True)),
                ('magic_power_place', models.BigIntegerField(db_index=True)),
                ('physic_power_place', models.BigIntegerField(db_index=True)),
                ('level_place', models.BigIntegerField(db_index=True)),
                ('phrases_count_place', models.BigIntegerField(db_index=True)),
                ('pvp_battles_1x1_number_place', models.BigIntegerField(db_index=True)),
                ('pvp_battles_1x1_victories_place', models.BigIntegerField(db_index=True)),
                ('referrals_number_place', models.IntegerField(default=0, db_index=True)),
                ('achievements_points_place', models.IntegerField(default=0, db_index=True)),
                ('help_count_place', models.IntegerField(default=0, db_index=True)),
                ('gifts_returned_place', models.IntegerField(default=0, db_index=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatingValues',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('might', models.FloatField(default=0, db_index=True)),
                ('bills_count', models.IntegerField(default=0, db_index=True)),
                ('magic_power', models.IntegerField(default=0, db_index=True)),
                ('physic_power', models.IntegerField(default=0, db_index=True)),
                ('level', models.IntegerField(default=0, db_index=True)),
                ('phrases_count', models.IntegerField(default=0, db_index=True)),
                ('pvp_battles_1x1_number', models.IntegerField(default=0, db_index=True)),
                ('pvp_battles_1x1_victories', models.FloatField(default=0.0, db_index=True)),
                ('referrals_number', models.IntegerField(default=0, db_index=True)),
                ('achievements_points', models.IntegerField(default=0, db_index=True)),
                ('help_count', models.IntegerField(default=0, db_index=True)),
                ('gifts_returned', models.IntegerField(default=0, db_index=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
