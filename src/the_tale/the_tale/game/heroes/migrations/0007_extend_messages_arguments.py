# -*- coding: utf-8 -*-


import json

from django.db import models, migrations


def append_variables_to_message(message):
    message.append(None)
    message.append({})
    return message


def update_messages(data):
    return [append_variables_to_message(message) for message in data]


def extend_messages_arguments(apps, schema_editor):
    Hero = apps.get_model("heroes", "Hero")

    for hero in Hero.objects.iterator():
        hero.messages = json.dumps({'messages': update_messages(json.loads(hero.messages)['messages'])}, ensure_ascii=False)
        hero.diary = json.dumps({'messages': update_messages(json.loads(hero.diary)['messages'])}, ensure_ascii=False)
        hero.save()


class Migration(migrations.Migration):

    dependencies = [
        ('heroes', '0006_auto_20150728_0920'),
    ]

    operations = [
        migrations.RunPython(
            extend_messages_arguments,
        ),
    ]
