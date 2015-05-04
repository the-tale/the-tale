# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import the_tale.common.utils.models
import rels.django
import django.utils.timezone
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('nick', models.CharField(default='', unique=True, max_length=128, db_index=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now=True, db_index=True)),
                ('premium_end_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), db_index=True)),
                ('active_end_at', models.DateTimeField(db_index=True)),
                ('premium_expired_notification_send_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), db_index=True)),
                ('is_fast', models.BooleanField(default=True, db_index=True)),
                ('is_bot', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True, null=True, blank=True)),
                ('new_messages_number', models.IntegerField(default=0)),
                ('last_news_remind_time', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('personal_messages_subscription', models.BooleanField(default=True)),
                ('news_subscription', models.BooleanField(default=True)),
                ('description', models.TextField(default='', blank=True)),
                ('ban_game_end_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), db_index=True)),
                ('ban_forum_end_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), db_index=True)),
                ('referer_domain', models.CharField(default=None, max_length=256, null=True, db_index=True)),
                ('referer', models.CharField(default=None, max_length=4096, null=True)),
                ('referrals_number', models.IntegerField(default=0)),
                ('action_id', models.CharField(default=None, max_length=128, null=True, db_index=True, blank=True)),
                ('permanent_purchases', models.TextField(default=b'[]')),
                ('might', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ['nick'],
                'permissions': (('moderate_account', '\u041c\u043e\u0436\u0435\u0442 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u044b \u0438 \u0442.\u043f.'),),
            },
            bases=(models.Model,),
        ),
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
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('account', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChangeCredentialsTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('comment', models.CharField(default=b'', max_length=256, null=True, blank=True)),
                ('old_email', models.EmailField(max_length=254, null=True)),
                ('new_email', models.EmailField(max_length=254, null=True)),
                ('new_password', models.TextField(default=None, null=True)),
                ('new_nick', models.CharField(default=None, max_length=128, null=True)),
                ('uuid', models.CharField(max_length=32, db_index=True)),
                ('relogin_required', models.BooleanField(default=False)),
                ('account', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RandomPremiumRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('days', models.IntegerField()),
                ('initiator', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResetPasswordTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_processed', models.BooleanField(default=False, db_index=True)),
                ('account', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
