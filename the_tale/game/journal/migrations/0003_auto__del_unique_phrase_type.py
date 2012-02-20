# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Phrase', fields ['type']
        db.delete_unique('journal_phrase', ['type'])


    def backwards(self, orm):
        
        # Adding unique constraint on 'Phrase', fields ['type']
        db.create_unique('journal_phrase', ['type'])


    models = {
        'journal.phrase': {
            'Meta': {'object_name': 'Phrase'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['journal']
