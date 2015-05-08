# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.TextField(default=b'{}')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('closed_at', models.DateTimeField(default=None, null=True, blank=True)),
                ('type', models.CharField(max_length=16, db_index=True)),
                ('good_uid', models.CharField(max_length=64, db_index=True)),
                ('group_id', models.IntegerField(default=0, db_index=True)),
                ('name', models.CharField(max_length=128, db_index=True)),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('price', models.IntegerField()),
                ('commission', models.IntegerField(default=0)),
                ('data', models.TextField(default=b'{}')),
                ('buyer', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('seller', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='lot',
            unique_together=set([('seller', 'good_uid')]),
        ),
    ]
