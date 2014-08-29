# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Template'
        db.create_table(u'linguistics_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('template', self.gf('django.db.models.fields.TextField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('state', self.gf('rels.django.RelationIntegerField')(db_index=True)),
            ('key', self.gf('rels.django.RelationIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'linguistics', ['Template'])

        # Adding unique constraint on 'Template', fields ['template', 'key', 'state']
        db.create_unique(u'linguistics_template', ['template', 'key', 'state'])


    def backwards(self, orm):
        # Removing unique constraint on 'Template', fields ['template', 'key', 'state']
        db.delete_unique(u'linguistics_template', ['template', 'key', 'state'])

        # Deleting model 'Template'
        db.delete_table(u'linguistics_template')


    models = {
        u'linguistics.template': {
            'Meta': {'unique_together': "(('template', 'key', 'state'),)", 'object_name': 'Template'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'linguistics.word': {
            'Meta': {'unique_together': "(('normal_form', 'type', 'state'),)", 'object_name': 'Word'},
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