# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def remove_keys(apps, schema_editor):
    Template = apps.get_model("linguistics", "Template")
    Template.objects.filter(key=560004).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0005_add_contributions_to_on_review_objects'),
    ]

    operations = [
        migrations.RunPython(
            remove_keys,
        ),
    ]
