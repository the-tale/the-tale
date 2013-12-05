# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GiveItemTask'
        db.create_table(u'collections_giveitemtask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Account'], null=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collections.Item'])),
        ))
        db.send_create_signal(u'collections', ['GiveItemTask'])

        # Adding model 'AccountItems'
        db.create_table(u'collections_accountitems', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Account'], unique=True)),
            ('items', self.gf('django.db.models.fields.TextField')(default='{}')),
        ))
        db.send_create_signal(u'collections', ['AccountItems'])


    def backwards(self, orm):
        # Deleting model 'GiveItemTask'
        db.delete_table(u'collections_giveitemtask')

        # Deleting model 'AccountItems'
        db.delete_table(u'collections_accountitems')


    models = {
        u'accounts.account': {
            'Meta': {'ordering': "['nick']", 'object_name': 'Account'},
            'active_end_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'ban_forum_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'ban_game_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'clan': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['clans.Clan']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_bot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_fast': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_news_remind_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'might': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'new_messages_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nick': ('django.db.models.fields.CharField', [], {'default': "u''", 'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'permanent_purchases': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'personal_messages_subscription': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'premium_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'premium_expired_notification_send_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'referer': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '4096', 'null': 'True'}),
            'referer_domain': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '256', 'null': 'True', 'db_index': 'True'}),
            'referral_of': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['accounts.Account']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'referrals_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
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
            'forum_subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum.SubCategory']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members_number': ('django.db.models.fields.IntegerField', [], {}),
            'motto': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        u'collections.accountitems': {
            'Meta': {'object_name': 'AccountItems'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.TextField', [], {'default': "'{}'"})
        },
        u'collections.collection': {
            'Meta': {'object_name': 'Collection'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'collections.giveitemtask': {
            'Meta': {'object_name': 'GiveItemTask'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Account']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collections.Item']"})
        },
        u'collections.item': {
            'Meta': {'object_name': 'Item'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collections.Kit']", 'on_delete': 'models.PROTECT'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'collections.kit': {
            'Meta': {'object_name': 'Kit'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collections.Collection']", 'on_delete': 'models.PROTECT'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'forum.category': {
            'Meta': {'object_name': 'Category'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        u'forum.subcategory': {
            'Meta': {'object_name': 'SubCategory'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum.Category']", 'on_delete': 'models.PROTECT'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_poster': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['accounts.Account']"}),
            'last_thread_created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'posts_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'restricted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'threads_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '16', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['collections']