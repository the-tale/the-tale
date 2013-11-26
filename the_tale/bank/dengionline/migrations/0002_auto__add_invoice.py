# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Invoice'
        db.create_table(u'dengionline_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('state', self.gf('rels.django.TableIntegerField')(null=True, db_index=True)),
            ('bank_type', self.gf('rels.django.TableIntegerField')(db_index=True)),
            ('bank_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('bank_currency', self.gf('rels.django.TableIntegerField')(db_index=True)),
            ('bank_amount', self.gf('django.db.models.fields.BigIntegerField')()),
            ('bank_invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bank.Invoice'], unique=True, null=True)),
            ('user_id', self.gf('django.db.models.fields.EmailField')(max_length=254, db_index=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=125)),
            ('payment_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('payment_currency', self.gf('rels.django.TableIntegerField')(db_index=True)),
            ('received_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2)),
            ('received_currency', self.gf('rels.django.TableIntegerField')(null=True, db_index=True)),
            ('paymode', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('payment_id', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True, null=True, db_index=True)),
        ))
        db.send_create_signal(u'dengionline', ['Invoice'])

    def backwards(self, orm):
        # Deleting model 'Invoice'
        db.delete_table(u'dengionline_invoice')

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
        u'dengionline.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'bank_amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_currency': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'bank_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'bank_invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bank.Invoice']", 'unique': 'True', 'null': 'True'}),
            'bank_type': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payment_currency': ('rels.django.TableIntegerField', [], {'db_index': 'True'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'paymode': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'received_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'received_currency': ('rels.django.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'state': ('rels.django.TableIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'db_index': 'True'})
        }
    }

    complete_apps = ['dengionline']