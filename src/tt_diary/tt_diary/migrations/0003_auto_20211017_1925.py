# Generated by Django 3.0.11 on 2021-10-17 19:25

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tt_diary', '0002_diary_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]