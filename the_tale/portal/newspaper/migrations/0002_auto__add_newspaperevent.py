# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NewspaperEvent'
        db.create_table('newspaper_newspaperevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('created_at_turn', self.gf('django.db.models.fields.IntegerField')()),
            ('data', self.gf('django.db.models.fields.TextField')(default=u'{}')),
        ))
        db.send_create_signal('newspaper', ['NewspaperEvent'])

    def backwards(self, orm):
        # Deleting model 'NewspaperEvent'
        db.delete_table('newspaper_newspaperevent')

    models = {
        'newspaper.newspaperevent': {
            'Meta': {'object_name': 'NewspaperEvent'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['newspaper']