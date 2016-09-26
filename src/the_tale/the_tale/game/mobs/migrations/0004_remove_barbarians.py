# -*- coding: utf-8 -*-


from django.db import models, migrations


def remove_barbarian_type(apps, schema_editor):
    Mob = apps.get_model("mobs", "MobRecord")

    Mob.objects.filter(type=0).update(is_mercenary=False, is_eatable=True)
    Mob.objects.filter(type=1).update(is_mercenary=False, is_eatable=True)
    Mob.objects.filter(type=2).update(is_mercenary=False, is_eatable=False)
    Mob.objects.filter(type=3).update(is_mercenary=False, is_eatable=False)
    Mob.objects.filter(type=4).update(is_mercenary=False, is_eatable=True)
    Mob.objects.filter(type=5).update(is_mercenary=True, is_eatable=True)
    Mob.objects.filter(type=6).update(is_mercenary=False, is_eatable=True)
    Mob.objects.filter(type=7).update(is_mercenary=False, is_eatable=True)
    Mob.objects.filter(type=8).update(is_mercenary=False, is_eatable=False)
    Mob.objects.filter(type=9).update(is_mercenary=False, is_eatable=False)
    Mob.objects.filter(type=10).update(is_mercenary=False, is_eatable=True)
    Mob.objects.filter(type=11).update(is_mercenary=False, is_eatable=True)

    Mob.objects.filter(type=4).update(type=5)


class Migration(migrations.Migration):

    dependencies = [
        ('mobs', '0003_auto_20150810_1506'),
    ]

    operations = [
        migrations.RunPython(
            remove_barbarian_type,
        ),
    ]
