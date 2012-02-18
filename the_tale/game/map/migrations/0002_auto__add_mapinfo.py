# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MapInfo'
        db.create_table('map_mapinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('turn_number', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
            ('terrain', self.gf('django.db.models.fields.TextField')(default='[]')),
        ))
        db.send_create_signal('map', ['MapInfo'])


    def backwards(self, orm):
        
        # Deleting model 'MapInfo'
        db.delete_table('map_mapinfo')


    models = {
        'map.mapinfo': {
            'Meta': {'object_name': 'MapInfo'},
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'terrain': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'turn_number': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['map']
