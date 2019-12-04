# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(unique=True, max_length=64, db_index=True)),
                ('value', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
