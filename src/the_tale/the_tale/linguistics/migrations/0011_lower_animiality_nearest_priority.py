# -*- coding: utf-8 -*-


import json

from django.db import models, migrations

from utg.migrations import m_0008_lower_animiality_nearest_priority


def migrate_words(apps, schema_editor):
    Word = apps.get_model("linguistics", "Word")

    for word in Word.objects.all():
        word_data = json.loads(word.forms)

        word_data = m_0008_lower_animiality_nearest_priority.migrate(word_data)

        word.forms = json.dumps(word_data, ensure_ascii=False)
        word.save()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0010_reduce_words_forms'),
    ]

    operations = [
        migrations.RunPython(
            migrate_words,
        ),
    ]
