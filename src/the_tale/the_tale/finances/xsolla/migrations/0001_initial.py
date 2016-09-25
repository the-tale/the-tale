# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('state', rels.django.RelationIntegerField(null=True, db_index=True)),
                ('bank_id', models.BigIntegerField()),
                ('bank_amount', models.BigIntegerField()),
                ('xsolla_id', models.CharField(max_length=255, db_index=True)),
                ('xsolla_v1', models.CharField(max_length=255)),
                ('xsolla_v2', models.CharField(max_length=200, null=True)),
                ('xsolla_v3', models.CharField(max_length=100, null=True)),
                ('comment', models.CharField(default='', max_length=255)),
                ('pay_result', rels.django.RelationIntegerField(null=True, db_index=True)),
                ('test', models.BooleanField(default=False)),
                ('date', models.DateTimeField(null=True)),
                ('request_url', models.CharField(max_length=1024)),
                ('bank_invoice', models.ForeignKey(related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, to='bank.Invoice', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('xsolla_id', 'test')]),
        ),
    ]
