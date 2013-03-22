# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):

        for map_info in orm['map.MapInfo'].objects.all():
            world = orm['map.WorldInfo'].objects.create()
            world.data = map_info.world
            world.save()

            map_info.world_link = world
            map_info.world = ''
            map_info.save()


    def backwards(self, orm):
        "Write your backwards methods here."


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
    symmetrical = True
