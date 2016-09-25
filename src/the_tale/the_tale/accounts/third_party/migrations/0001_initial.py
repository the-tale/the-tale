# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import the_tale.common.utils.models
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uid', the_tale.common.utils.models.UUIDField(unique=True, max_length=36, db_index=True)),
                ('application_name', models.CharField(max_length=100)),
                ('application_info', models.CharField(max_length=100)),
                ('application_description', models.TextField()),
                ('state', rels.django.RelationIntegerField()),
                ('account', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
