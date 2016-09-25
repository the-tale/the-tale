# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section', models.CharField(default=None, max_length=16, db_index=True, choices=[(b'test', '\u0422\u0435\u0441\u0442'), (b'world', '\u041c\u0438\u0444\u043e\u043b\u043e\u0433\u0438\u044f'), (b'development', '\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430')])),
                ('slug', models.CharField(default=b'', max_length=256, db_index=True, blank=True)),
                ('caption', models.CharField(max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('description', models.TextField(default=b'')),
                ('content', models.TextField(default=b'')),
                ('order', models.IntegerField(default=None, db_index=True, blank=True)),
                ('active', models.BooleanField(default=False)),
                ('author', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('editor', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('section', 'slug'), ('section', 'order')]),
        ),
    ]
