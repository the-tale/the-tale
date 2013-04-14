# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'NewspaperEvent'
        db.delete_table(u'newspaper_newspaperevent')

    def backwards(self, orm):
        # Adding model 'NewspaperEvent'
        db.create_table(u'newspaper_newspaperevent', (
            ('type', self.gf('django.db.models.fields.IntegerField')(null=True, db_index=True)),
            ('created_at_turn', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True, db_index=True)),
            ('section', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default=u'{}')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('newspaper', ['NewspaperEvent'])

    models = {
        
    }

    complete_apps = ['newspaper']