# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('length', models.FloatField(default=0.0, blank=True)),
                ('exists', models.BooleanField(default=True)),
                ('path', models.TextField(default=b'')),
                ('point_1', models.ForeignKey(related_name='+', to='places.Place', on_delete=models.CASCADE)),
                ('point_2', models.ForeignKey(related_name='+', to='places.Place', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Waymark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('length', models.FloatField(default=0.0, blank=True)),
                ('point_from', models.ForeignKey(related_name='+', to='places.Place', on_delete=models.PROTECT)),
                ('point_to', models.ForeignKey(related_name='+', to='places.Place', on_delete=models.PROTECT)),
                ('road', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to='roads.Road', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='waymark',
            unique_together=set([('point_from', 'point_to', 'road')]),
        ),
        migrations.AlterUniqueTogether(
            name='road',
            unique_together=set([('point_1', 'point_2')]),
        ),
    ]
