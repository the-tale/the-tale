# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0007_auto_20150604_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='forms',
            field=models.TextField(db_index=True),
        ),
    ]
