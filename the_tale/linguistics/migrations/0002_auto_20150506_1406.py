# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='parent',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='linguistics.Template'),
        ),
        migrations.AlterField(
            model_name='word',
            name='parent',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='linguistics.Word'),
        ),
    ]
