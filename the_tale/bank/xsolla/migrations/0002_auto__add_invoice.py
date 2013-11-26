# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Invoice'
        db.create_table(u'xsolla_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('state', self.gf('rels.django.TableIntegerField')(null=True, db_index=True)),
            ('bank_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('bank_amount', self.gf('django.db.models.fields.BigIntegerField')()),
            ('bank_invoice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', unique=True, null=True, to=orm['bank.Invoice'])),
            ('xsolla_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('xsolla_v1', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('xsolla_v2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('xsolla_v3', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('pay_result', self.gf('rels.django.TableIntegerField')(null=True, db_index=True)),
            ('test', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'xsolla', ['Invoice'])

    def backwards(self, orm):
        # Deleting model 'Invoice'
        db.delete_table(u'xsolla_invoice')

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
            'Meta': {'object_name': 'Invoice'},
            'bank_amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'unique': 'True', 'null': 'True', 'to': u"orm['bank.Invoice']"}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pay_result': ('rels.django.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'state': ('rels.django.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'xsolla_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'xsolla_v1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'xsolla_v2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'xsolla_v3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['xsolla']