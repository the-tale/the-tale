# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Place'
        db.create_table('places_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('x', self.gf('django.db.models.fields.BigIntegerField')()),
            ('y', self.gf('django.db.models.fields.BigIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('subtype', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('places', ['Place'])


    def backwards(self, orm):
        
        # Deleting model 'Place'
        db.delete_table('places_place')


    models = {
        'places.place': {
            'Meta': {'object_name': 'Place'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['places']
