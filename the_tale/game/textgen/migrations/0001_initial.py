# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Word'
        db.create_table('textgen_word', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('normalized', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('forms', self.gf('django.db.models.fields.TextField')()),
            ('properties', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('textgen', ['Word'])

        # Adding model 'Template'
        db.create_table('textgen_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('textgen', ['Template'])


    def backwards(self, orm):
        
        # Deleting model 'Word'
        db.delete_table('textgen_word')

        # Deleting model 'Template'
        db.delete_table('textgen_template')


    models = {
        'textgen.template': {
            'Meta': {'object_name': 'Template'},
            'data': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'})
        },
        'textgen.word': {
            'Meta': {'object_name': 'Word'},
            'forms': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'normalized': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'properties': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['textgen']
