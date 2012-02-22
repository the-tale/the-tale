# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ArtifactConstructor.gender'
        db.add_column('artifacts_artifactconstructor', 'gender', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ArtifactConstructor.gender'
        db.delete_column('artifacts_artifactconstructor', 'gender')


    models = {
        'artifacts.artifactconstructor': {
            'Meta': {'object_name': 'ArtifactConstructor'},
            'equip_type': ('django.db.models.fields.IntegerField', [], {}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['artifacts']
