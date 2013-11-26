# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Invoice', fields ['xsolla_id']
        db.delete_unique(u'xsolla_invoice', ['xsolla_id'])

        # Adding field 'Invoice.date'
        db.add_column(u'xsolla_invoice', 'date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Invoice.request_url'
        db.add_column(u'xsolla_invoice', 'request_url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1024),
                      keep_default=False)

        # Adding unique constraint on 'Invoice', fields ['test', 'xsolla_id']
        db.create_unique(u'xsolla_invoice', ['test', 'xsolla_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'Invoice', fields ['test', 'xsolla_id']
        db.delete_unique(u'xsolla_invoice', ['test', 'xsolla_id'])

        # Deleting field 'Invoice.date'
        db.delete_column(u'xsolla_invoice', 'date')

        # Deleting field 'Invoice.request_url'
        db.delete_column(u'xsolla_invoice', 'request_url')

        # Adding unique constraint on 'Invoice', fields ['xsolla_id']
        db.create_unique(u'xsolla_invoice', ['xsolla_id'])

    models = {
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
        },
        u'xsolla.invoice': {
            'Meta': {'unique_together': "(('xsolla_id', 'test'),)", 'object_name': 'Invoice'},
            'bank_amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'unique': 'True', 'null': 'True', 'to': u"orm['bank.Invoice']"}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pay_result': ('rels.django.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'request_url': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'state': ('rels.django.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'xsolla_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'xsolla_v1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'xsolla_v2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'xsolla_v3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['xsolla']