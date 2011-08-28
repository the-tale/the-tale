# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'HeroPosition'
        db.delete_table('places_heroposition')


    def backwards(self, orm):
        
        # Adding model 'HeroPosition'
        db.create_table('places_heroposition', (
            ('invert_direction', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('hero', self.gf('django.db.models.fields.related.OneToOneField')(related_name='position', unique=True, to=orm['heroes.Hero'])),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='positions', null=True, to=orm['places.Place'], blank=True)),
            ('percents', self.gf('django.db.models.fields.FloatField')(default=None, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('road', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='positions', null=True, to=orm['roads.Road'], blank=True)),
        ))
        db.send_create_signal('places', ['HeroPosition'])


    models = {
        'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
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

    complete_apps = ['places']
