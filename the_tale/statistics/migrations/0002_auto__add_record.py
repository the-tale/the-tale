# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Record'
        db.create_table(u'statistics_record', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('type', self.gf('rels.django.RelationIntegerField')(db_index=True)),
            ('value_int', self.gf('django.db.models.fields.BigIntegerField')()),
            ('value_float', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'statistics', ['Record'])


    def backwards(self, orm):
        # Deleting model 'Record'
        db.delete_table(u'statistics_record')


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