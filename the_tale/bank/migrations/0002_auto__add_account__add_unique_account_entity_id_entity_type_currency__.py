# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = ( ("accounts", "0001_initial"), )

    def forwards(self, orm):
        # Adding model 'Account'
        db.create_table(u'bank_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('entity_type', self.gf('rels.django_staff.TableIntegerField')(db_index=True)),
            ('entity_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('currency', self.gf('rels.django_staff.TableIntegerField')(db_index=True)),
            ('amount', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal(u'bank', ['Account'])

        # Adding unique constraint on 'Account', fields ['entity_id', 'entity_type', 'currency']
        db.create_unique(u'bank_account', ['entity_id', 'entity_type', 'currency'])

        # Adding model 'Invoice'
        db.create_table(u'bank_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('recipient_type', self.gf('rels.django_staff.TableIntegerField')(db_index=True)),
            ('recipient_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('sender_type', self.gf('rels.django_staff.TableIntegerField')(db_index=True)),
            ('sender_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('state', self.gf('rels.django_staff.TableIntegerField')(db_index=True)),
            ('currency', self.gf('rels.django_staff.TableIntegerField')(db_index=True)),
            ('amount', self.gf('django.db.models.fields.BigIntegerField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'bank', ['Invoice'])

    def backwards(self, orm):
        # Removing unique constraint on 'Account', fields ['entity_id', 'entity_type', 'currency']
        db.delete_unique(u'bank_account', ['entity_id', 'entity_type', 'currency'])

        # Deleting model 'Account'
        db.delete_table(u'bank_account')

        # Deleting model 'Invoice'
        db.delete_table(u'bank_invoice')

    models = {
        u'bank.account': {
            'Meta': {'unique_together': "(('entity_id', 'entity_type', 'currency'),)", 'object_name': 'Account'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'entity_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'entity_type': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'bank.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'recipient_type': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'sender_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'sender_type': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django_staff.TableIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['bank']
