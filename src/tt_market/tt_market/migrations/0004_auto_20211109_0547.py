# Generated by Django 3.1.13 on 2021-11-09 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tt_market', '0003_auto_20211018_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logrecord',
            name='data',
            field=models.JSONField(default=dict),
        ),
    ]
