# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='person',
            field=models.OneToOneField(to='persons.Person'),
        ),
        migrations.AlterField(
            model_name='place',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
