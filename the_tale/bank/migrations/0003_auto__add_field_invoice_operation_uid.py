# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Invoice.operation_uid'
        db.add_column(u'bank_invoice', 'operation_uid',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, db_index=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Invoice.operation_uid'
        db.delete_column(u'bank_invoice', 'operation_uid')

    models = {
        u'bank.account': {
            'Meta': {'unique_together': "(('entity_id', 'entity_type', 'currency'),)", 'object_name': 'Account'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'entity_type': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'bank.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation_uid': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'recipient_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'recipient_type': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'sender_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sender_type': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['bank']