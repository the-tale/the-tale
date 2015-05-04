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
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField(default=b'', blank=True)),
                ('hide_from_sender', models.BooleanField(default=False)),
                ('hide_from_recipient', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created_at',
            },
            bases=(models.Model,),
        ),
    ]
