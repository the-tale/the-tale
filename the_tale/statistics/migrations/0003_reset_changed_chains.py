# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        Record = orm['statistics.Record']

        Record.objects.filter(type=26).delete()
        Record.objects.filter(type=84).delete()
        Record.objects.filter(type=85).delete()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'statistics.record': {
            'Meta': {'object_name': 'Record'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'value_float': ('django.db.models.fields.FloatField', [], {}),
            'value_int': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['statistics']
    symmetrical = True
