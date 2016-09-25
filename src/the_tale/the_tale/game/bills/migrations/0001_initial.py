# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('voting_end_at', models.DateTimeField(null=True, blank=True)),
                ('created_at_turn', models.IntegerField()),
                ('applyed_at_turn', models.IntegerField(null=True)),
                ('ends_at_turn', models.BigIntegerField(db_index=True, null=True, blank=True)),
                ('ended_at', models.DateTimeField(null=True, blank=True)),
                ('duration', rels.django.RelationIntegerField()),
                ('caption', models.CharField(max_length=256)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('approved_by_moderator', models.BooleanField(default=False, db_index=True)),
                ('rationale', models.TextField(blank=True)),
                ('technical_data', models.TextField(default={}, blank=True)),
                ('chronicle_on_accepted', models.TextField(default='', blank=True)),
                ('chronicle_on_ended', models.TextField(default='', blank=True)),
                ('votes_for', models.IntegerField(default=0)),
                ('votes_against', models.IntegerField(default=0)),
                ('votes_refrained', models.IntegerField(default=0)),
                ('min_votes_percents_required', models.FloatField(default=0.0)),
                ('is_declined', models.BooleanField(default=False)),
                ('declined_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='bills.Bill', null=True)),
                ('forum_thread', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='forum.Thread', null=True)),
                ('owner', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('remove_initiator', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('moderate_bill', '\u041c\u043e\u0436\u0435\u0442 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0437\u0430\u043a\u043e\u043d\u043e\u043f\u0440\u043e\u0435\u043a\u0442\u044b'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('bill', models.ForeignKey(to='bills.Bill')),
                ('owner', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('owner', 'bill')]),
        ),
        migrations.AddField(
            model_name='actor',
            name='bill',
            field=models.ForeignKey(to='bills.Bill'),
            preserve_default=True,
        ),
    ]
