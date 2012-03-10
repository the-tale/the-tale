# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Person.gender'
        db.add_column('persons_person', 'gender', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Person.gender'
        db.delete_column('persons_person', 'gender')


    models = {
        'persons.person': {
            'Meta': {'object_name': 'Person'},
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'to': "orm['places.Place']"}),
            'power': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': '{}'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'terrain': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '1'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['persons']
