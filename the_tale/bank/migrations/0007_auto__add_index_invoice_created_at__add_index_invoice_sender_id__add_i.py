# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Invoice', fields ['created_at']
        db.create_index(u'bank_invoice', ['created_at'])

        # Adding index on 'Invoice', fields ['sender_id']
        db.create_index(u'bank_invoice', ['sender_id'])

        # Adding index on 'Invoice', fields ['updated_at']
        db.create_index(u'bank_invoice', ['updated_at'])

        # Adding index on 'Invoice', fields ['recipient_id']
        db.create_index(u'bank_invoice', ['recipient_id'])


    def backwards(self, orm):
        # Removing index on 'Invoice', fields ['recipient_id']
        db.delete_index(u'bank_invoice', ['recipient_id'])

        # Removing index on 'Invoice', fields ['updated_at']
        db.delete_index(u'bank_invoice', ['updated_at'])

        # Removing index on 'Invoice', fields ['sender_id']
        db.delete_index(u'bank_invoice', ['sender_id'])

        # Removing index on 'Invoice', fields ['created_at']
        db.delete_index(u'bank_invoice', ['created_at'])


    models = {
        u'bank.account': {
            'Meta': {'unique_together': "(('entity_id', 'entity_type', 'currency'),)", 'object_name': 'Account'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'entity_type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'bank.invoice': {
            'Meta': {'object_name': 'Invoice', 'index_together': "(('recipient_type', 'recipient_id', 'currency'), ('sender_type', 'sender_id', 'currency'))"},
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'currency': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'description_for_recipient': ('django.db.models.fields.TextField', [], {}),
            'description_for_sender': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation_uid': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'recipient_id': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'recipient_type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'sender_id': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'sender_type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['bank']