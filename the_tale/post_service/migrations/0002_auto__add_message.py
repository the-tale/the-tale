# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Message'
        db.create_table(u'post_service_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('processed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('state', self.gf('rels.django.RelationIntegerField')(db_index=True)),
            ('handler', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'post_service', ['Message'])

    def backwards(self, orm):
        # Deleting model 'Message'
        db.delete_table(u'post_service_message')

    models = {
        u'post_service.message': {
            'Meta': {'object_name': 'Message'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'handler': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['post_service']