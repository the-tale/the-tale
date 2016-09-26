# -*- coding: utf-8 -*-


from django.db import models, migrations, transaction


def create_contributions(apps, schema_editor):
    Word = apps.get_model("linguistics", "Word")
    Template = apps.get_model("linguistics", "Template")
    Contribution = apps.get_model("linguistics", "Contribution")

    for word in Word.objects.all():
        if word.author_id is None:
            continue

        if word.state == 1:
            continue

        with transaction.atomic():
            try:
                Contribution.objects.create(account_id=word.author_id,
                                            state=word.state,
                                            type=0,
                                            source=0,
                                            entity_id=word.id)
            except:
                pass

    for template in Template.objects.all():
        if template.author_id is None:
            continue

        if template.state == 1:
            continue

        with transaction.atomic():
            try:
                Contribution.objects.create(account_id=template.author_id,
                                            state=template.state,
                                            type=1,
                                            source=0,
                                            entity_id=template.id)
            except:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0004_auto_20150528_1611'),
    ]

    operations = [
        migrations.RunPython(
            create_contributions,
        ),
    ]
