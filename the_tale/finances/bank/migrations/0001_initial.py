# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('entity_type', rels.django.RelationIntegerField(db_index=True)),
                ('entity_id', models.BigIntegerField()),
                ('currency', rels.django.RelationIntegerField(db_index=True)),
                ('amount', models.BigIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('recipient_type', rels.django.RelationIntegerField(db_index=True)),
                ('recipient_id', models.BigIntegerField(db_index=True)),
                ('sender_type', rels.django.RelationIntegerField(db_index=True)),
                ('sender_id', models.BigIntegerField(db_index=True)),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('currency', rels.django.RelationIntegerField(db_index=True)),
                ('amount', models.BigIntegerField()),
                ('operation_uid', models.CharField(max_length=64, db_index=True)),
                ('description_for_recipient', models.TextField()),
                ('description_for_sender', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='invoice',
            index_together=set([('recipient_type', 'recipient_id', 'currency'), ('sender_type', 'sender_id', 'currency')]),
        ),
        migrations.AlterUniqueTogether(
            name='account',
            unique_together=set([('entity_id', 'entity_type', 'currency')]),
        ),
    ]
