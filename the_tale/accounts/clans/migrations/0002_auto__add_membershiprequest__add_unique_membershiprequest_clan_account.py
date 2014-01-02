# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MembershipRequest'
        db.create_table(u'clans_membershiprequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('clan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clans.Clan'])),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Account'])),
            ('type', self.gf('rels.django.RelationIntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=1024)),
        ))
        db.send_create_signal(u'clans', ['MembershipRequest'])

        # Adding unique constraint on 'MembershipRequest', fields ['clan', 'account']
        db.create_unique(u'clans_membershiprequest', ['clan_id', 'account_id'])

        # Adding model 'Membership'
        db.create_table(u'clans_membership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('clan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clans.Clan'], on_delete=models.PROTECT)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Account'], unique=True, on_delete=models.PROTECT)),
            ('role', self.gf('rels.django.RelationIntegerField')()),
        ))
        db.send_create_signal(u'clans', ['Membership'])

        # Adding model 'Clan'
        db.create_table(u'clans_clan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('abbr', self.gf('django.db.models.fields.CharField')(unique=True, max_length=5)),
            ('motto', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2024)),
            ('members_number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'clans', ['Clan'])


    def backwards(self, orm):
        # Removing unique constraint on 'MembershipRequest', fields ['clan', 'account']
        db.delete_unique(u'clans_membershiprequest', ['clan_id', 'account_id'])

        # Deleting model 'MembershipRequest'
        db.delete_table(u'clans_membershiprequest')

        # Deleting model 'Membership'
        db.delete_table(u'clans_membership')

        # Deleting model 'Clan'
        db.delete_table(u'clans_clan')


    models = {
        u'accounts.account': {
            'Meta': {'ordering': "['nick']", 'object_name': 'Account'},
            'active_end_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'ban_forum_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'ban_game_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_fast': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_news_remind_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'new_messages_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nick': ('django.db.models.fields.CharField', [], {'default': "u''", 'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'personal_messages_subscription': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'premium_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'premium_expired_notification_send_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'referer': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '4096', 'null': 'True'}),
            'referer_domain': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '256', 'null': 'True', 'db_index': 'True'}),
            'referral_of': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['accounts.Account']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'referrals_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'clans.clan': {
            'Meta': {'object_name': 'Clan'},
            'abbr': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members_number': ('django.db.models.fields.IntegerField', [], {}),
            'motto': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        u'clans.membership': {
            'Meta': {'object_name': 'Membership'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']", 'unique': 'True', 'on_delete': 'models.PROTECT'}),
            'clan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clans.Clan']", 'on_delete': 'models.PROTECT'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('rels.django.RelationIntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'clans.membershiprequest': {
            'Meta': {'unique_together': "(('clan', 'account'),)", 'object_name': 'MembershipRequest'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']"}),
            'clan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clans.Clan']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'type': ('rels.django.RelationIntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['clans']