# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def remove_companion_rarity_restriction(apps, schema_editor):
    Restriction = apps.get_model("linguistics", "Restriction")

    Restriction.objects.filter(group=16).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0013_remove_companion_type'),
    ]

    operations = [
        migrations.RunPython(
            remove_companion_rarity_restriction,
        ),
    ]
