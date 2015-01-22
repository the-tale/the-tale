# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CompanionRecord.type'
        db.add_column(u'companions_companionrecord', 'type',
                      self.gf('rels.django.RelationIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'CompanionRecord.dedication'
        db.add_column(u'companions_companionrecord', 'dedication',
                      self.gf('rels.django.RelationIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'CompanionRecord.rarity'
        db.add_column(u'companions_companionrecord', 'rarity',
                      self.gf('rels.django.RelationIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'CompanionRecord.max_health'
        db.add_column(u'companions_companionrecord', 'max_health',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CompanionRecord.type'
        db.delete_column(u'companions_companionrecord', 'type')

        # Deleting field 'CompanionRecord.dedication'
        db.delete_column(u'companions_companionrecord', 'dedication')

        # Deleting field 'CompanionRecord.rarity'
        db.delete_column(u'companions_companionrecord', 'rarity')

        # Deleting field 'CompanionRecord.max_health'
        db.delete_column(u'companions_companionrecord', 'max_health')


    models = {
        u'companions.companionrecord': {
            'Meta': {'object_name': 'CompanionRecord'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'dedication': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_health': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'rarity': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['companions']