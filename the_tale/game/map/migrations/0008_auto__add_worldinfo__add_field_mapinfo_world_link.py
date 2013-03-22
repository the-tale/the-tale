# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WorldInfo'
        db.create_table('map_worldinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('map', ['WorldInfo'])

        # Adding field 'MapInfo.world_link'
        db.add_column('map_mapinfo', 'world_link',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['map.WorldInfo'], null=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'WorldInfo'
        db.delete_table('map_worldinfo')

        # Deleting field 'MapInfo.world_link'
        db.delete_column('map_mapinfo', 'world_link_id')

    models = {
        'map.mapinfo': {
            'Meta': {'object_name': 'MapInfo'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'statistics': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'terrain': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'turn_number': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {}),
            'world': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'world_link': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['map.WorldInfo']", 'null': 'True'})
        },
        'map.worldinfo': {
            'Meta': {'object_name': 'WorldInfo'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['map']