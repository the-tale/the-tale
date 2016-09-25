# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import rels.django
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(max_length=256)),
                ('slug', models.CharField(max_length=32, db_index=True)),
                ('order', models.IntegerField(default=0, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('account', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_at_turn', models.BigIntegerField(default=0)),
                ('updated_at', models.DateTimeField(default=None, auto_now=True, null=True)),
                ('updated_at_turn', models.BigIntegerField(default=0)),
                ('text', models.TextField(default=b'', blank=True)),
                ('markup_method', rels.django.RelationIntegerField()),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('removed_by', rels.django.RelationIntegerField(default=None, null=True)),
                ('technical', models.BooleanField(default=False)),
                ('author', models.ForeignKey(related_name='forum_posts', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('remove_initiator', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('moderate_post', '\u041c\u043e\u0436\u0435\u0442 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('caption', models.CharField(max_length=256)),
                ('order', models.IntegerField(default=0, blank=True)),
                ('uid', models.CharField(default=None, max_length=16, null=True, db_index=True, blank=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('last_thread_created_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('threads_count', models.IntegerField(default=0)),
                ('posts_count', models.BigIntegerField(default=0)),
                ('closed', models.BooleanField(default=False)),
                ('restricted', models.BooleanField(default=False, db_index=True)),
                ('description', models.TextField(default='')),
                ('category', models.ForeignKey(to='forum.Category', on_delete=django.db.models.deletion.PROTECT)),
                ('last_poster', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubCategoryReadInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('all_read_at', models.DateTimeField()),
                ('read_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('subcategory', models.ForeignKey(to='forum.SubCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('subcategory', models.ForeignKey(to='forum.SubCategory', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('caption', models.CharField(max_length=256)),
                ('posts_count', models.BigIntegerField(default=0)),
                ('updated_at', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), auto_now_add=True)),
                ('technical', models.BooleanField(default=False)),
                ('important', models.BooleanField(default=False, db_index=True)),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_poster', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('subcategory', models.ForeignKey(to='forum.SubCategory', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'permissions': (('moderate_thread', '\u041c\u043e\u0436\u0435\u0442 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0442\u0435\u043c\u044b \u043d\u0430 \u0444\u043e\u0440\u0443\u043c\u0435'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ThreadReadInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('account', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('thread', models.ForeignKey(to='forum.Thread')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='threadreadinfo',
            unique_together=set([('thread', 'account')]),
        ),
        migrations.AddField(
            model_name='subscription',
            name='thread',
            field=models.ForeignKey(to='forum.Thread', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('account', 'subcategory'), ('account', 'thread')]),
        ),
        migrations.AlterUniqueTogether(
            name='subcategoryreadinfo',
            unique_together=set([('subcategory', 'account')]),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='last_thread',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='forum.Thread', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(to='forum.Thread', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permission',
            name='subcategory',
            field=models.ForeignKey(to='forum.SubCategory'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together=set([('subcategory', 'account')]),
        ),
    ]
