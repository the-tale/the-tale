# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import rels.django


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(max_length=256)),
                ('description', models.TextField(default=b'', blank=True)),
                ('content', models.TextField(default=b'', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('emailed', rels.django.RelationIntegerField(db_index=True)),
                ('forum_thread', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='forum.Thread', null=True)),
            ],
            options={
                'get_latest_by': 'created_at',
                'permissions': (('edit_news', '\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c \u043d\u043e\u0432\u043e\u0441\u0442\u0438'),),
            },
            bases=(models.Model,),
        ),
    ]
