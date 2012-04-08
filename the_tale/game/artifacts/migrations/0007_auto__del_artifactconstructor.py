# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ArtifactConstructor'
        db.delete_table('artifacts_artifactconstructor')

    def backwards(self, orm):
        # Adding model 'ArtifactConstructor'
        db.create_table('artifacts_artifactconstructor', (
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64)),
            ('equip_type', self.gf('django.db.models.fields.IntegerField')()),
            ('item_type', self.gf('django.db.models.fields.IntegerField')()),
            ('normalized_name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True, db_index=True)),
        ))
        db.send_create_signal('artifacts', ['ArtifactConstructor'])

    models = {
        
    }

    complete_apps = ['artifacts']