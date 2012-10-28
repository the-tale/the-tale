# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NewspaperEvent.type'
        db.add_column('newspaper_newspaperevent', 'type',
                      self.gf('django.db.models.fields.IntegerField')(null=True, db_index=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'NewspaperEvent.type'
        db.delete_column('newspaper_newspaperevent', 'type')

    models = {
        'newspaper.newspaperevent': {
            'Meta': {'object_name': 'NewspaperEvent'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['newspaper']