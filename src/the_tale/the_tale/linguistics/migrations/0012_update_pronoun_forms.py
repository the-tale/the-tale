# -*- coding: utf-8 -*-


import json

from django.db import models, migrations


from utg.migrations import m_0009_pronoun_modernization


def migrate_words(apps, schema_editor):
    Word = apps.get_model("linguistics", "Word")

    for word in Word.objects.all():
        word_data = json.loads(word.forms)

        word_data = m_0009_pronoun_modernization.migrate(word_data)

        word.forms = json.dumps(word_data, ensure_ascii=False)
        word.save()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0011_lower_animiality_nearest_priority'),
    ]

    operations = [
        migrations.RunPython(
            migrate_words,
        ),
    ]
