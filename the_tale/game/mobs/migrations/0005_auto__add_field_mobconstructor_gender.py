# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'MobConstructor.gender'
        db.add_column('mobs_mobconstructor', 'gender', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'MobConstructor.gender'
        db.delete_column('mobs_mobconstructor', 'gender')


    models = {
        'mobs.mobconstructor': {
            'Meta': {'object_name': 'MobConstructor'},
            'abilities': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'damage_dispersion': ('django.db.models.fields.FloatField', [], {}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'health_relative_to_hero': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiative': ('django.db.models.fields.FloatField', [], {}),
            'loot_list': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'power_per_level': ('django.db.models.fields.FloatField', [], {}),
            'terrain': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '1', 'db_index': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['mobs']
