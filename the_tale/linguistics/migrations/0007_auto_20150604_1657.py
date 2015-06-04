# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0006_remove_unnecessary_keys'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='template',
            options={'permissions': (('moderate_template', '\u041c\u043e\u0436\u0435\u0442 \u043c\u043e\u0434\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0448\u0430\u0431\u043b\u043e\u043d\u044b \u0444\u0440\u0430\u0437'), ('edit_template', '\u041c\u043e\u0436\u0435\u0442 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0448\u0430\u0431\u043b\u043e\u043d\u044b \u0444\u0440\u0430\u0437'))},
        ),
    ]
