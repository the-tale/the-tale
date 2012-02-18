# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MobConstructor'
        db.create_table('mobs_mobconstructor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64)),
            ('health_relative_to_hero', self.gf('django.db.models.fields.FloatField')()),
            ('initiative', self.gf('django.db.models.fields.FloatField')()),
            ('power_per_level', self.gf('django.db.models.fields.FloatField')()),
            ('damage_dispersion', self.gf('django.db.models.fields.FloatField')()),
            ('abilities', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('loot_list', self.gf('django.db.models.fields.TextField')(default='[]')),
        ))
        db.send_create_signal('mobs', ['MobConstructor'])


    def backwards(self, orm):
        
        # Deleting model 'MobConstructor'
        db.delete_table('mobs_mobconstructor')


    models = {
        'mobs.mobconstructor': {
            'Meta': {'object_name': 'MobConstructor'},
            'abilities': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'damage_dispersion': ('django.db.models.fields.FloatField', [], {}),
            'health_relative_to_hero': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiative': ('django.db.models.fields.FloatField', [], {}),
            'loot_list': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'power_per_level': ('django.db.models.fields.FloatField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['mobs']
