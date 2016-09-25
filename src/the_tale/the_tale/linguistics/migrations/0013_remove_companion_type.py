# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models, migrations


def get_restriction_id(model, group, external_id):
    try:
        return model.objects.get(group=group, external_id=external_id).id
    except model.DoesNotExist:
        return None

def fix_restrictions(restrictions, removed, added):
    return [(r if r[1] != removed else (r[0], added)) for r in restrictions]


def remove_companion_type(apps, schema_editor):
    Template = apps.get_model("linguistics", "Template")

    Restriction = apps.get_model("linguistics", "Restriction")

    # TODO: check if not exists
    living_restriction = get_restriction_id(Restriction, group=14, external_id=0)
    construct_restriction = get_restriction_id(Restriction, group=14, external_id=1)
    unusual_restriction = get_restriction_id(Restriction, group=14, external_id=2)
    barbarian_restriction = get_restriction_id(Restriction, group=10, external_id=4)

    civilized_restriction = get_restriction_id(Restriction, group=10, external_id=5)
    mechanical_restriction = get_restriction_id(Restriction, group=10, external_id=3)
    supernatural_restriction = get_restriction_id(Restriction, group=10, external_id=2)


    for template in Template.objects.all():
        data = json.loads(template.data)

        restrictions = data.get('restrictions')

        if not restrictions:
            continue

        restrictions = fix_restrictions(restrictions, living_restriction, civilized_restriction)
        restrictions = fix_restrictions(restrictions, construct_restriction, mechanical_restriction)
        restrictions = fix_restrictions(restrictions, unusual_restriction, supernatural_restriction)
        restrictions = fix_restrictions(restrictions, barbarian_restriction, civilized_restriction)

        data['restrictions'] = restrictions

        template.data = json.dumps(data, ensure_ascii=False)
        template.save()

    Restriction.objects.filter(group=14).delete()



class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0012_update_pronoun_forms'),
    ]

    operations = [
        migrations.RunPython(
            remove_companion_type,
        ),
    ]
