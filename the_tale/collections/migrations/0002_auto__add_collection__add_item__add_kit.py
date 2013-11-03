# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Collection'
        db.create_table(u'collections_collection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1000)),
        ))
        db.send_create_signal(u'collections', ['Collection'])

        # Adding model 'Item'
        db.create_table(u'collections_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('kit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collections.Kit'], on_delete=models.PROTECT)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'collections', ['Item'])

        # Adding model 'Kit'
        db.create_table(u'collections_kit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collections.Collection'], on_delete=models.PROTECT)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1000)),
        ))
        db.send_create_signal(u'collections', ['Kit'])


    def backwards(self, orm):
        # Deleting model 'Collection'
        db.delete_table(u'collections_collection')

        # Deleting model 'Item'
        db.delete_table(u'collections_item')

        # Deleting model 'Kit'
        db.delete_table(u'collections_kit')


    models = {
        u'collections.collection': {
            'Meta': {'object_name': 'Collection'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'collections.item': {
            'Meta': {'object_name': 'Item'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collections.Kit']", 'on_delete': 'models.PROTECT'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'collections.kit': {
            'Meta': {'object_name': 'Kit'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collections.Collection']", 'on_delete': 'models.PROTECT'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['collections']