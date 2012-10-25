# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Page.author'
        db.delete_column('cms_page', 'author_id')

        # Deleting field 'Page.editor'
        db.delete_column('cms_page', 'editor_id')

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Page.author'
        raise RuntimeError("Cannot reverse this migration. 'Page.author' and its values cannot be restored.")
        # Adding field 'Page.editor'
        db.add_column('cms_page', 'editor',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['auth.User']),
                      keep_default=False)

    models = {
        'cms.page': {
            'Meta': {'unique_together': "(('section', 'slug'), ('section', 'order'))", 'object_name': 'Page'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'db_index': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '16', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'db_index': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['cms']