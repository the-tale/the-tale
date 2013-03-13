# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Building'
        db.create_table('places_building', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('x', self.gf('django.db.models.fields.BigIntegerField')()),
            ('y', self.gf('django.db.models.fields.BigIntegerField')()),
            ('type', self.gf('rels.django_staff.TableIntegerField')()),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Place'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['persons.Person'])),
        ))
        db.send_create_signal('places', ['Building'])

        # Deleting field 'Place.type'
        db.delete_column('places_place', 'type')

    def backwards(self, orm):
        # Deleting model 'Building'
        db.delete_table('places_building')

        # Adding field 'Place.type'
        db.add_column('places_place', 'type',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

    models = {
        'persons.person': {
            'Meta': {'object_name': 'Person'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'enemies_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'out_game_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'to': "orm['places.Place']"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('rels.django_staff.TableIntegerField', [], {})
        },
        'places.building': {
            'Meta': {'object_name': 'Building'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['persons.Person']"}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['places.Place']"}),
            'type': ('rels.django_staff.TableIntegerField', [], {}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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