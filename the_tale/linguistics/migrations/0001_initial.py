# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rels.django
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('type', rels.django.RelationIntegerField(default=0, db_index=True)),
                ('source', rels.django.RelationIntegerField(db_index=True)),
                ('entity_id', models.BigIntegerField(db_index=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Restriction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('name', models.CharField(max_length=128)),
                ('group', rels.django.RelationIntegerField(db_index=True)),
                ('external_id', models.BigIntegerField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('raw_template', models.TextField(db_index=True)),
                ('data', models.TextField()),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('key', rels.django.RelationIntegerField(db_index=True)),
                ('errors_status', rels.django.RelationIntegerField(default=0, db_index=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='linguistics.Template', unique=True)),
            ],
            options={
                'permissions': (('moderate_template', '\u041c\u043e\u0436\u0435\u0442 \u043c\u043e\u0434\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0448\u0430\u0431\u043b\u043e\u043d\u044b \u0444\u0440\u0430\u0437'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemplateRestriction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('variable', models.CharField(max_length=32, db_index=True)),
                ('restriction', models.ForeignKey(to='linguistics.Restriction')),
                ('template', models.ForeignKey(to='linguistics.Template')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('normal_form', models.CharField(max_length=64)),
                ('forms', models.TextField()),
                ('state', rels.django.RelationIntegerField(db_index=True)),
                ('type', rels.django.RelationIntegerField(db_index=True)),
                ('used_in_ingame_templates', models.IntegerField(default=0)),
                ('used_in_onreview_templates', models.IntegerField(default=0)),
                ('used_in_status', rels.django.RelationIntegerField(default=2, db_index=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='linguistics.Word', unique=True)),
            ],
            options={
                'permissions': (('moderate_word', '\u041c\u043e\u0436\u0435\u0442 \u043c\u043e\u0434\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0441\u043b\u043e\u0432\u0430'),),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='word',
            unique_together=set([('normal_form', 'type', 'state')]),
        ),
        migrations.AlterUniqueTogether(
            name='templaterestriction',
            unique_together=set([('restriction', 'template', 'variable')]),
        ),
        migrations.AlterUniqueTogether(
            name='restriction',
            unique_together=set([('group', 'external_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='contribution',
            unique_together=set([('type', 'account', 'entity_id')]),
        ),
    ]
