# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobs', '0002_auto_20150724_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobrecord',
            name='is_eatable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mobrecord',
            name='is_mercenary',
            field=models.BooleanField(default=False),
        ),
    ]
