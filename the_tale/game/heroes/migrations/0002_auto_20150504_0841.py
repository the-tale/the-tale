# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mobs', '0001_initial'),
        ('places', '0001_initial'),
        ('persons', '0001_initial'),
        ('heroes', '0001_initial'),
        ('roads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='heropreferences',
            name='enemy',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='persons.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heropreferences',
            name='friend',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='persons.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heropreferences',
            name='hero',
            field=models.ForeignKey(to='heroes.Hero'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heropreferences',
            name='mob',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='mobs.MobRecord', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heropreferences',
            name='place',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='places.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hero',
            name='account',
            field=models.ForeignKey(related_name='heroes', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hero',
            name='pos_place',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='places.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hero',
            name='pos_previous_place',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='places.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hero',
            name='pos_road',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='roads.Road', null=True),
            preserve_default=True,
        ),
    ]
