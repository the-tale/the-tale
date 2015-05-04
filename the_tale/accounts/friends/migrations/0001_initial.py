# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('text', models.TextField(default='\u0414\u0430\u0432\u0430\u0439\u0442\u0435 \u0434\u0440\u0443\u0436\u0438\u0442\u044c')),
                ('is_confirmed', models.BooleanField(default=False, db_index=True)),
                ('friend_1', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('friend_2', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
