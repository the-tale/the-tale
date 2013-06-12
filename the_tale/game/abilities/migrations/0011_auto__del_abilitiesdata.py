# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'AbilitiesData'
        db.delete_table(u'abilities_abilitiesdata')

    def backwards(self, orm):
        # Adding model 'AbilitiesData'
        db.create_table(u'abilities_abilitiesdata', (
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Hero'])),
            ('arena_pvp_1x1_leave_queue_available_at', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('building_repair_available_at', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('help_available_at', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('arena_pvp_1x1_available_at', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
        ))
        db.send_create_signal('abilities', ['AbilitiesData'])

    models = {
        
    }

    complete_apps = ['abilities']