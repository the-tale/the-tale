# -*- coding: utf-8 -*-

import json

from django.db import models, migrations


def scale_power(apps, schema_editor):
    Person = apps.get_model("persons", "Person")
    for person in Person.objects.all():
        data = json.loads(person.data)
        if 'power_points' in data:
            data['power_points'] = [(turn, power / 10) for turn, power in data['power_points']]
        person.data = json.dumps(data)
        person.save()

class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0003_auto_20150506_1406'),
    ]

    operations = [
        migrations.RunPython(scale_power),
    ]
