# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Road'
        db.create_table('roads_road', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('point_1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['places.Place'])),
            ('point_2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['places.Place'])),
            ('length', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('roads', ['Road'])

        # Adding unique constraint on 'Road', fields ['point_1', 'point_2']
        db.create_unique('roads_road', ['point_1_id', 'point_2_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Road', fields ['point_1', 'point_2']
        db.delete_unique('roads_road', ['point_1_id', 'point_2_id'])

        # Deleting model 'Road'
        db.delete_table('roads_road')


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
        },
        'roads.road': {
            'Meta': {'unique_together': "(('point_1', 'point_2'),)", 'object_name': 'Road'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'point_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"}),
            'point_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"})
        }
    }

    complete_apps = ['roads']
