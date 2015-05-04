# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0002_auto_20150504_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hero',
            name='saved_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='hero',
            name='ui_caching_started_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
