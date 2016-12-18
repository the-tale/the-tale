# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0002_metaactionmember_hero'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MetaAction',
        ),
        migrations.RemoveField(
            model_name='metaactionmember',
            name='action',
        ),
        migrations.RemoveField(
            model_name='metaactionmember',
            name='hero',
        ),
        migrations.DeleteModel(
            name='MetaActionMember',
        ),
    ]
