# -*- coding: utf-8 -*-
import datetime
import json

from south.db import db
from south.v2 import DataMigration
from django.db import models


WORDS = {0: (u'кузница', (u'жр',)),
         1: (u'домик рыболова', (u'мр',)),
         2: (u'мастерская портного', (u'жр',)),
         3: (u'лесопилка', (u'жр',)),
         4: (u'домик охотника', (u'мр',)),
         5: (u'сторожевая башня', (u'жр',)),
         6: (u'торговый пост', (u'мр',)),
         7: (u'трактир', (u'мр',)),
         8: (u'логово вора', (u'ср',)),
         9: (u'ферма', (u'жр',)),
         10: (u'шахта', (u'жр',)),
         11: (u'храм', (u'мр',)),
         12: (u'больница', (u'жр',)),
         13: (u'лаборатория', (u'жр',)),
         14: (u'плаха', (u'жр',)),
         15: (u'башня мага', (u'жр',)),
         16: (u'ратуша', (u'жр',)),
         17: (u'бюро', (u'ср',)),
         18: (u'поместье', (u'ср',)),
         19: (u'сцена', (u'жр',)),
         20: (u'конюшни', (u'жр', u'мн')),
         21: (u'ранчо', (u'ср',))}


class Migration(DataMigration):

    def forms(self, name, properties):
        data = { 'forms': [name]*12,
                 'type': 1,
                 'normalized': name,
                 'properties': properties}
        return json.dumps(data)

    def forwards(self, orm):

        for building in orm['places.Building'].objects.all():
            building.name_forms = self.forms(*WORDS[building.type])
            building.save()


    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        u'persons.person': {
            'Meta': {'object_name': 'Person'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'enemies_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'out_game_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'to': u"orm['places.Place']"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('rels.django.RelationIntegerField', [], {})
        },
        u'places.building': {
            'Meta': {'object_name': 'Building'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integrity': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['persons.Person']", 'unique': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['places.Place']"}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'updated_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['places']
    symmetrical = True
