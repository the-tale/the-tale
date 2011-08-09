# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Waymark'
        db.create_table('roads_waymark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('point_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['places.Place'])),
            ('point_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['places.Place'])),
            ('road', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['roads.Road'])),
        ))
        db.send_create_signal('roads', ['Waymark'])

        # Adding unique constraint on 'Waymark', fields ['point_from', 'point_to', 'road']
        db.create_unique('roads_waymark', ['point_from_id', 'point_to_id', 'road_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Waymark', fields ['point_from', 'point_to', 'road']
        db.delete_unique('roads_waymark', ['point_from_id', 'point_to_id', 'road_id'])

        # Deleting model 'Waymark'
        db.delete_table('roads_waymark')


    models = {
        'places.place': {
            'Meta': {'object_name': 'Place'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'terrain': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '1'}),
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
        },
        'roads.waymark': {
            'Meta': {'unique_together': "(('point_from', 'point_to', 'road'),)", 'object_name': 'Waymark'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'point_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"}),
            'point_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"}),
            'road': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['roads.Road']"})
        }
    }

    complete_apps = ['roads']
