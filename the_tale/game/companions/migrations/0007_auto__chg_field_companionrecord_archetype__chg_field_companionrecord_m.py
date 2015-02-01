# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'CompanionRecord.archetype'
        db.alter_column(u'companions_companionrecord', 'archetype', self.gf('rels.django.RelationIntegerField')(default=0))

        # Changing field 'CompanionRecord.mode'
        db.alter_column(u'companions_companionrecord', 'mode', self.gf('rels.django.RelationIntegerField')(default=0))

    def backwards(self, orm):

        # Changing field 'CompanionRecord.archetype'
        db.alter_column(u'companions_companionrecord', 'archetype', self.gf('rels.django.RelationIntegerField')(null=True))

        # Changing field 'CompanionRecord.mode'
        db.alter_column(u'companions_companionrecord', 'mode', self.gf('rels.django.RelationIntegerField')(null=True))

    models = {
        u'companions.companionrecord': {
            'Meta': {'object_name': 'CompanionRecord'},
            'archetype': ('rels.django.RelationIntegerField', [], {'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'dedication': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_health': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'mode': ('rels.django.RelationIntegerField', [], {'blank': 'True'}),
            'rarity': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['companions']