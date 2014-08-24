# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Word'
        db.create_table(u'linguistics_word', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('normal_form', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('forms', self.gf('django.db.models.fields.TextField')()),
            ('state', self.gf('rels.django.RelationIntegerField')(db_index=True)),
            ('type', self.gf('rels.django.RelationIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'linguistics', ['Word'])


    def backwards(self, orm):
        # Deleting model 'Word'
        db.delete_table(u'linguistics_word')


    models = {
        u'linguistics.word': {
            'Meta': {'object_name': 'Word'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'forms': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'normal_form': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['linguistics']