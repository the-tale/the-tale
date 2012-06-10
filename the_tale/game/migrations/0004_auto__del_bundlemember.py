# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'BundleMember'
        db.delete_table('game_bundlemember')

        # Removing M2M table for field members on 'Bundle'
        db.delete_table('game_bundle_members')

    def backwards(self, orm):
        # Adding model 'BundleMember'
        db.create_table('game_bundlemember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('angel', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bundle', null=True, to=orm['angels.Angel'])),
        ))
        db.send_create_signal('game', ['BundleMember'])

        # Adding M2M table for field members on 'Bundle'
        db.create_table('game_bundle_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bundle', models.ForeignKey(orm['game.bundle'], null=False)),
            ('bundlemember', models.ForeignKey(orm['game.bundlemember'], null=False))
        ))
        db.create_unique('game_bundle_members', ['bundle_id', 'bundlemember_id'])

    models = {
        'game.bundle': {
            'Meta': {'object_name': 'Bundle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'game.time': {
            'Meta': {'object_name': 'Time'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'turn_number': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['game']