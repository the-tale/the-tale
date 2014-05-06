# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Place.tax'
        db.add_column(u'places_place', 'tax',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)


        # Changing field 'ResourceExchange.place_2'
        db.alter_column(u'places_resourceexchange', 'place_2_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['places.Place']))

        # Changing field 'ResourceExchange.place_1'
        db.alter_column(u'places_resourceexchange', 'place_1_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['places.Place']))

    def backwards(self, orm):
        # Deleting field 'Place.tax'
        db.delete_column(u'places_place', 'tax')


        # User chose to not deal with backwards NULL issues for 'ResourceExchange.place_2'
        raise RuntimeError("Cannot reverse this migration. 'ResourceExchange.place_2' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'ResourceExchange.place_2'
        db.alter_column(u'places_resourceexchange', 'place_2_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Place']))

        # User chose to not deal with backwards NULL issues for 'ResourceExchange.place_1'
        raise RuntimeError("Cannot reverse this migration. 'ResourceExchange.place_1' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'ResourceExchange.place_1'
        db.alter_column(u'places_resourceexchange', 'place_1_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['places.Place']))

    models = {
        u'accounts.account': {
            'Meta': {'ordering': "['nick']", 'object_name': 'Account'},
            'action_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
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
        u'bills.bill': {
            'Meta': {'object_name': 'Bill'},
            'approved_by_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {}),
            'declined_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['bills.Bill']", 'blank': 'True', 'null': 'True'}),
            'duration': ('rels.django.RelationIntegerField', [], {}),
            'ended_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ends_at_turn': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'forum_thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['forum.Thread']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'min_votes_percents_required': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['accounts.Account']"}),
            'rationale': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reject_reason': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'remove_initiator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['accounts.Account']"}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'technical_data': ('django.db.models.fields.TextField', [], {'default': '{}', 'blank': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'votes_against': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votes_for': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votes_refrained': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'voting_end_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
            'description': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_poster': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['accounts.Account']"}),
            'last_thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['forum.Thread']"}),
            'last_thread_created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'posts_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'restricted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'threads_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'uid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '16', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'forum.thread': {
            'Meta': {'object_name': 'Thread'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['accounts.Account']"}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'important': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'last_poster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['accounts.Account']"}),
            'posts_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum.SubCategory']", 'on_delete': 'models.PROTECT'}),
            'technical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'persons.person': {
            'Meta': {'object_name': 'Person'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'enemies_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('rels.django.RelationIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'out_game_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'on_delete': 'models.PROTECT', 'to': u"orm['places.Place']"}),
            'race': ('rels.django.RelationIntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('rels.django.RelationIntegerField', [], {})
        },
        u'places.building': {
            'Meta': {'object_name': 'Building'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integrity': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['persons.Person']", 'unique': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['places.Place']"}),
            'state': ('rels.django.RelationIntegerField', [], {'db_index': 'True'}),
            'type': ('rels.django.RelationIntegerField', [], {}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'expected_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'freedom': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'goods': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('rels.django.RelationIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'persons_changed_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'production': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'race': ('rels.django.RelationIntegerField', [], {}),
            'safety': ('django.db.models.fields.FloatField', [], {'default': '0.75'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'transport': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'places.resourceexchange': {
            'Meta': {'object_name': 'ResourceExchange'},
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['bills.Bill']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['places.Place']"}),
            'place_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['places.Place']"}),
            'resource_1': ('rels.django.RelationIntegerField', [], {}),
            'resource_2': ('rels.django.RelationIntegerField', [], {})
        }
    }

    complete_apps = ['places']