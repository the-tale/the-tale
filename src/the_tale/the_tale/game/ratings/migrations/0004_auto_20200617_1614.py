# Generated by Django 3.0.7 on 2020-06-17 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0003_auto_20200605_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratingplaces',
            name='help_count_place',
        ),
        migrations.RemoveField(
            model_name='ratingvalues',
            name='help_count',
        ),
    ]
