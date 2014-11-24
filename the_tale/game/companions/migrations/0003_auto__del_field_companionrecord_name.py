# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'CompanionRecord.name'
        db.delete_column(u'companions_companionrecord', 'name')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'CompanionRecord.name'
        raise RuntimeError("Cannot reverse this migration. 'CompanionRecord.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'CompanionRecord.name'
        db.add_column(u'companions_companionrecord', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length=32, unique=True, db_index=True),
                      keep_default=False)


    models = {
        u'companions.companionrecord': {
            'Meta': {'object_name': 'CompanionRecord'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['companions']