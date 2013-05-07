# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'PostponedTask.internal_uuid'
        db.delete_column(u'postponed_tasks_postponedtask', 'internal_uuid')

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'PostponedTask.internal_uuid'
        raise RuntimeError("Cannot reverse this migration. 'PostponedTask.internal_uuid' and its values cannot be restored.")
    models = {
        u'postponed_tasks.postponedtask': {
            'Meta': {'object_name': 'PostponedTask'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'internal_result': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'internal_state': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'internal_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'live_time': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['postponed_tasks']