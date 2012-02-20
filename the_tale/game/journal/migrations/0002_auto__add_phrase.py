# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Phrase'
        db.create_table('journal_phrase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('template', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('journal', ['Phrase'])


    def backwards(self, orm):
        
        # Deleting model 'Phrase'
        db.delete_table('journal_phrase')


    models = {
        'journal.phrase': {
            'Meta': {'object_name': 'Phrase'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['journal']
