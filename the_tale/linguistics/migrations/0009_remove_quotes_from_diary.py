# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models, migrations

DIARY_KEYS = (0,
              3,
              4,
              17,
              20001,
              20002,
              20003,
              40000,
              40001,
              40002,
              40003,
              40004,
              40005,
              40006,
              40007,
              40008,
              40009,
              40010,
              40011,
              40012,
              40013,
              40014,
              40015,
              40016,
              40017,
              40018,
              40019,
              40020,
              40021,
              40022,
              40023,
              40024,
              40025,
              40026,
              40027,
              40028,
              40029,
              40030,
              40031,
              80001,
              80002,
              80003,
              80004,
              80005,
              80006,
              80007,
              80008,
              80009,
              80010,
              80011,
              80012,
              80013,
              80014,
              80015,
              80016,
              80017,
              80018,
              80019,
              80020,
              80021,
              80022,
              80023,
              80024,
              80027,
              80028,
              80034,
              80035,
              300000,
              360019,
              360020,
              360021,
              360022,
              360023,
              360024,
              360025,
              360026,
              360027,
              380013,
              380014,
              380015,
              380016,
              380017,
              380018,
              380019,
              380020,
              380021,
              400017,
              400018,
              400019,
              400020,
              400021,
              400022,
              400023,
              400024,
              400025,
              400026,
              400027,
              400028,
              400029,
              420004,
              420005,
              420006,
              420007,
              420008,
              440004,
              440005,
              440006,
              460007,
              460008,
              460009,
              480006,
              480007,
              480008,
              500004,
              500005,
              500006,
              520004,
              520005,
              520006,
              540002,
              540003,
              540004,
              540005,
              540006,
              540007,
              540008,
              540009,
              540010,
              540011,
              540012,
              540013,
              540014,
              540015,
              560019,
              560020,
              560021,
              560022,
              560023,
              560024,
              560025,
              560026,
              560027,
              560028,
              560029,
              560030,
              560031,
              560032,
              560033,
              580000,
              580001,
              580002,
              580005 )


def remove_quotes(apps, schema_editor):
    Template = apps.get_model("linguistics", "Template")

    for template in Template.objects.filter(key__in=DIARY_KEYS):
        if template.raw_template[0] != u'«':
            continue

        if template.raw_template[-1] == u'»':
            processor = lambda text: text[1:-1]

        elif template.raw_template[-2:] == u'».':
            processor = lambda text: text[1:-2] + u'.'

        else:
            continue

        data = json.loads(template.data)

        template.raw_template = processor(template.raw_template)

        for verificator in data['verificators']:
            verificator['text'] = processor(verificator['text'])

        data['template']['template'] = processor(data['template']['template'])

        template.data = json.dumps(data)
        template.save()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0008_auto_20150727_1600'),
    ]

    operations = [
        migrations.RunPython(
            remove_quotes,
        ),
    ]
