# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Word', fields ['normal_form', 'type', 'state']
        db.create_unique(u'linguistics_word', ['normal_form', 'type', 'state'])


    def backwards(self, orm):
        # Removing unique constraint on 'Word', fields ['normal_form', 'type', 'state']
        db.delete_unique(u'linguistics_word', ['normal_form', 'type', 'state'])


    models = {
        u'linguistics.word': {
            'Meta': {'unique_together': "(('normal_form', 'type', 'state'),)", 'object_name': 'Word'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'forms': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'normal_form': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['linguistics']