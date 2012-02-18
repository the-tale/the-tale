# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ArtifactConstructor'
        db.create_table('artifacts_artifactconstructor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('item_type', self.gf('django.db.models.fields.IntegerField')()),
            ('equip_type', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64)),
        ))
        db.send_create_signal('artifacts', ['ArtifactConstructor'])


    def backwards(self, orm):
        
        # Deleting model 'ArtifactConstructor'
        db.delete_table('artifacts_artifactconstructor')


    models = {
        'artifacts.artifactconstructor': {
            'Meta': {'object_name': 'ArtifactConstructor'},
            'equip_type': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'})
        }
    }

    complete_apps = ['artifacts']
