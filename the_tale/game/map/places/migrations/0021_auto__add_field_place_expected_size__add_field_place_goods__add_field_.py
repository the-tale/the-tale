# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Place.expected_size'
        db.add_column(u'places_place', 'expected_size',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Place.goods'
        db.add_column(u'places_place', 'goods',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Place.production'
        db.add_column(u'places_place', 'production',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Place.sefety'
        db.add_column(u'places_place', 'sefety',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Place.freedom'
        db.add_column(u'places_place', 'freedom',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Place.transport'
        db.add_column(u'places_place', 'transport',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Place.expected_size'
        db.delete_column(u'places_place', 'expected_size')

        # Deleting field 'Place.goods'
        db.delete_column(u'places_place', 'goods')

        # Deleting field 'Place.production'
        db.delete_column(u'places_place', 'production')

        # Deleting field 'Place.sefety'
        db.delete_column(u'places_place', 'sefety')

        # Deleting field 'Place.freedom'
        db.delete_column(u'places_place', 'freedom')

        # Deleting field 'Place.transport'
        db.delete_column(u'places_place', 'transport')

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
            'type': ('rels.django.TableIntegerField', [], {})
        },
        u'places.building': {
            'Meta': {'object_name': 'Building'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integrity': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['persons.Person']", 'unique': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['places.Place']"}),
            'state': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.TableIntegerField', [], {}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'expected_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'freedom': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'goods': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'production': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sefety': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'transport': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'updated_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['places']