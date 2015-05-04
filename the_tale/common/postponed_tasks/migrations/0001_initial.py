# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PostponedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('live_time', models.BigIntegerField(default=None, null=True)),
                ('state', models.IntegerField(default=0, db_index=True, choices=[(0, '\u043e\u0436\u0438\u0434\u0430\u0435\u0442 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0438'), (1, '\u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u0430'), (2, '\u0441\u0431\u0440\u043e\u0448\u0435\u043d\u0430'), (3, '\u043e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u0438 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0435'), (4, '\u0438\u0441\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u043f\u0440\u0438 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0435'), (5, '\u043f\u0440\u0435\u0432\u044b\u0448\u0435\u043d\u043e \u0432\u0440\u0435\u043c\u044f \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f')])),
                ('comment', models.TextField(default=b'', blank=True)),
                ('internal_result', models.IntegerField(db_index=True, null=True, choices=[(0, '\u0443\u0434\u0430\u0447\u043d\u043e\u0435 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435'), (1, '\u043e\u0448\u0438\u0431\u043a\u0430'), (2, '\u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435'), (3, '\u043e\u0436\u0438\u0434\u0430\u0435\u0442 \u0434\u0440\u0443\u0433\u0438\u0445 \u0437\u0430\u0434\u0430\u0447')])),
                ('internal_type', models.CharField(max_length=64, db_index=True)),
                ('internal_state', models.IntegerField(db_index=True)),
                ('internal_data', models.TextField(default='{}')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
