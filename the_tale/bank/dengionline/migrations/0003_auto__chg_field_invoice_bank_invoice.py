# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Invoice.bank_invoice'
        db.alter_column(u'dengionline_invoice', 'bank_invoice_id', self.gf('django.db.models.fields.related.ForeignKey')(unique=True, null=True, on_delete=models.SET_NULL, to=orm['bank.Invoice']))

    def backwards(self, orm):

        # Changing field 'Invoice.bank_invoice'
        db.alter_column(u'dengionline_invoice', 'bank_invoice_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bank.Invoice'], unique=True, null=True))

    models = {
        u'bank.invoice': {
            'Meta': {'object_name': 'Invoice', 'index_together': "(('recipient_type', 'recipient_id', 'currency'), ('sender_type', 'sender_id', 'currency'))"},
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation_uid': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'recipient_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'recipient_type': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'sender_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sender_type': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dengionline.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'bank_amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_currency': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'bank_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['bank.Invoice']"}),
            'bank_type': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payment_currency': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'paymode': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'received_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'received_currency': ('rels.django_staff.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'state': ('rels.django_staff.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'db_index': 'True'})
        }
    }

    complete_apps = ['dengionline']