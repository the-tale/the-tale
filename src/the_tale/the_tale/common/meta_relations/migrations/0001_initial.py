# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation', models.IntegerField(db_index=True)),
                ('from_type', models.IntegerField()),
                ('from_object', models.BigIntegerField()),
                ('to_type', models.IntegerField()),
                ('to_object', models.BigIntegerField()),
            ],
        ),
        migrations.AlterIndexTogether(
            name='relation',
            index_together=set([('to_type', 'to_object'), ('from_type', 'from_object')]),
        ),
    ]
