# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0003_auto_20150506_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='actual_bills',
            field=models.TextField(default=b'[]'),
        ),
    ]
