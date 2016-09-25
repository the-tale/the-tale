# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def remove_building_destroyed_by_amortization_templates(apps, schema_editor):
    Template = apps.get_model("linguistics", "Template")
    Template.objects.filter(key=260009).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0002_auto_20150506_1406'),
    ]

    operations = [
        migrations.RunPython(remove_building_destroyed_by_amortization_templates),
    ]
