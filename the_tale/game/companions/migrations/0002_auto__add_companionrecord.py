# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CompanionRecord'
        db.create_table(u'companions_companionrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('state', self.gf('rels.django.RelationIntegerField')(db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='{}')),
        ))
        db.send_create_signal(u'companions', ['CompanionRecord'])


    def backwards(self, orm):
        # Deleting model 'CompanionRecord'
        db.delete_table(u'companions_companionrecord')


    models = {
        u'companions.companionrecord': {
            'Meta': {'object_name': 'CompanionRecord'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['companions']