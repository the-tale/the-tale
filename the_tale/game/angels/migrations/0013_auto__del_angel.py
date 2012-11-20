# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('heroes', '0041_auto__del_field_hero_angel'),
        ('abilities', '0006_auto__del_field_abilitytask_angel'),
        ('game', '0010_auto__del_field_bundlemember_angel__chg_field_bundlemember_account')
    )

    def forwards(self, orm):
        # Deleting model 'Angel'
        db.delete_table('angels_angel')

    def backwards(self, orm):
        # Adding model 'Angel'
        db.create_table('angels_angel', (
            ('account', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['accounts.Account'], unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('angels', ['Angel'])

    models = {

    }

    complete_apps = ['angels']
