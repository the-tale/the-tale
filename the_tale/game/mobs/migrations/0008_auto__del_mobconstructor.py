# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'MobConstructor'
        db.delete_table('mobs_mobconstructor')

    def backwards(self, orm):
        # Adding model 'MobConstructor'
        db.create_table('mobs_mobconstructor', (
            ('abilities', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('loot_list', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('power_per_level', self.gf('django.db.models.fields.FloatField')()),
            ('terrain', self.gf('django.db.models.fields.CharField')(default='.', max_length=1, db_index=True)),
            ('damage_dispersion', self.gf('django.db.models.fields.FloatField')()),
            ('initiative', self.gf('django.db.models.fields.FloatField')()),
            ('health_relative_to_hero', self.gf('django.db.models.fields.FloatField')()),
            ('normalized_name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64, unique=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=64)),
        ))
        db.send_create_signal('mobs', ['MobConstructor'])

    models = {
        
    }

    complete_apps = ['mobs']