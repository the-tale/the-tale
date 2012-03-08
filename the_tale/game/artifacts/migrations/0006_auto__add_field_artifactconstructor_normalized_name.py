# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ArtifactConstructor.normalized_name'
        db.add_column('artifacts_artifactconstructor', 'normalized_name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ArtifactConstructor.normalized_name'
        db.delete_column('artifacts_artifactconstructor', 'normalized_name')


    models = {
        'artifacts.artifactconstructor': {
            'Meta': {'object_name': 'ArtifactConstructor'},
            'equip_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'normalized_name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['artifacts']
