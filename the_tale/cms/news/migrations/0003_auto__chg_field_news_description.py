# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Renaming column for 'News.description' to match new field type.
        db.rename_column('news_news', 'description_id', 'description')
        # Changing field 'News.description'
        db.alter_column('news_news', 'description', self.gf('django.db.models.fields.TextField')())

        # Removing index on 'News', fields ['description']
        db.delete_index('news_news', ['description_id'])


    def backwards(self, orm):
        
        # Adding index on 'News', fields ['description']
        db.create_index('news_news', ['description_id'])

        # Renaming column for 'News.description' to match new field type.
        db.rename_column('news_news', 'description', 'description_id')
        # Changing field 'News.description'
        db.alter_column('news_news', 'description_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Content']))


    models = {
        'news.news': {
            'Meta': {'object_name': 'News'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['news']
