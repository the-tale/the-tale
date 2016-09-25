# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pvp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle1x1',
            name='account',
            field=models.OneToOneField(related_name='+', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='battle1x1',
            name='enemy',
            field=models.OneToOneField(related_name='+', null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
