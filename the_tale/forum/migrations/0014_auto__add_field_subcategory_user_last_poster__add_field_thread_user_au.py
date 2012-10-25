# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SubCategory.user_last_poster'
        db.add_column('forum_subcategory', 'user_last_poster',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Thread.user_author'
        db.add_column('forum_thread', 'user_author',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Thread.user_last_poster'
        db.add_column('forum_thread', 'user_last_poster',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Post.user_author'
        db.add_column('forum_post', 'user_author',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Post.user_remove_initiator'
        db.add_column('forum_post', 'user_remove_initiator',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['auth.User']),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'SubCategory.user_last_poster'
        db.delete_column('forum_subcategory', 'user_last_poster_id')

        # Deleting field 'Thread.user_author'
        db.delete_column('forum_thread', 'user_author_id')

        # Deleting field 'Thread.user_last_poster'
        db.delete_column('forum_thread', 'user_last_poster_id')

        # Deleting field 'Post.user_author'
        db.delete_column('forum_post', 'user_author_id')

        # Deleting field 'Post.user_remove_initiator'
        db.delete_column('forum_post', 'user_remove_initiator_id')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forum.category': {
            'Meta': {'object_name': 'Category'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'forum.post': {
            'Meta': {'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup_method': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'remove_initiator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'removed_by': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'technical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Thread']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'user_author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_remove_initiator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'forum.subcategory': {
            'Meta': {'object_name': 'SubCategory'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Category']"}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_poster': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'posts_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'threads_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'user_last_poster': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'forum.thread': {
            'Meta': {'object_name': 'Thread'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_poster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'posts_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.SubCategory']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'user_author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_last_poster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['forum']