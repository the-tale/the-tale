# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PostponedTask'
        db.create_table('postponed_tasks_postponedtask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('live_time', self.gf('django.db.models.fields.BigIntegerField')(default=None, null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('internal_type', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('internal_uuid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('internal_state', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('internal_data', self.gf('django.db.models.fields.TextField')(default=u'{}')),
        ))
        db.send_create_signal('postponed_tasks', ['PostponedTask'])

    def backwards(self, orm):
        # Deleting model 'PostponedTask'
        db.delete_table('postponed_tasks_postponedtask')

    models = {
        'postponed_tasks.postponedtask': {
            'Meta': {'object_name': 'PostponedTask'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'internal_state': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'internal_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'internal_uuid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'live_time': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['postponed_tasks']