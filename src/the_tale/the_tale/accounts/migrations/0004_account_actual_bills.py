# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20150506_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='actual_bills',
            field=models.TextField(default=b'[]'),
        ),
    ]
