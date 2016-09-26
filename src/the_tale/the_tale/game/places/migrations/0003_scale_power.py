# -*- coding: utf-8 -*-

import json

from django.db import models, migrations


def scale_power(apps, schema_editor):
    Place = apps.get_model("places", "Place")
    for place in Place.objects.all():
        data = json.loads(place.data)
        if 'power_points' in data:
            data['power_points'] = [(turn, power / 10) for turn, power in data['power_points']]
        place.data = json.dumps(data)
        place.save()


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0002_auto_20150506_1406'),
    ]

    operations = [
        migrations.RunPython(scale_power),
    ]
