# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Action.created_at_turn'
        db.add_column('actions_action', 'created_at_turn',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'Action.hero_health_lost'
        db.add_column('actions_action', 'hero_health_lost',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Action.created_at_turn'
        db.delete_column('actions_action', 'created_at_turn')

        # Deleting field 'Action.hero_health_lost'
        db.delete_column('actions_action', 'hero_health_lost')

    models = {
        'accounts.account': {
            'Meta': {'ordering': "['nick']", 'object_name': 'Account'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_fast': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'last_news_remind_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'new_messages_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nick': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'actions.action': {
            'Meta': {'object_name': 'Action'},
            'back': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'break_at': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Bundle']"}),
            'context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'destination_x': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'destination_y': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'extra_probability': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['heroes.Hero']"}),
            'hero_health_lost': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'meta_action': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['actions.MetaAction']", 'null': 'True'}),
            'mob': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'mob_context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'percents': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'percents_barier': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['places.Place']"}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quests.Quest']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'uninitialized'", 'max_length': '50'}),
            'textgen_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'actions.metaaction': {
            'Meta': {'object_name': 'MetaAction'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percents': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'uninitialized'", 'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'actions.metaactionmember': {
            'Meta': {'object_name': 'MetaActionMember'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['actions.MetaAction']"}),
            'context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'game.bundle': {
            'Meta': {'object_name': 'Bundle'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'abilities': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'account': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'heroes'", 'null': 'True', 'blank': 'True', 'to': "orm['accounts.Account']"}),
            'actions_descriptions': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'active_state_end_at': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bag': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'destiny_points_spend': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'diary': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'energy': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'equipment': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'experience': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'health': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_fast': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'last_action_percents': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'last_energy_regeneration_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'messages': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'might': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'might_updated_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'money': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'next_spending': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'pos_from_x': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_from_y': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_invert_direction': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'pos_percents': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_place': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': "orm['places.Place']"}),
            'pos_road': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': "orm['roads.Road']"}),
            'pos_to_x': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_to_y': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pref_enemy': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': "orm['persons.Person']"}),
            'pref_enemy_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_energy_regeneration_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'pref_energy_regeneration_type_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_equipment_slot': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'pref_equipment_slot_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_friend': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': "orm['persons.Person']"}),
            'pref_friend_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_mob_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_mob_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'pref_place': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': "orm['places.Place']"}),
            'pref_place_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'quests_history': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'raw_power': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_artifacts_had': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_loot_had': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_earned_from_artifacts': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_earned_from_help': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_earned_from_loot': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_earned_from_quests': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_spend_for_artifacts': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_spend_for_heal': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_spend_for_impact': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_spend_for_sharpening': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_money_spend_for_useless': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_pve_deaths': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_pve_kills': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_quests_done': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        },
        'persons.person': {
            'Meta': {'object_name': 'Person'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'enemies_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'to': "orm['places.Place']"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'updated_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'quests.quest': {
            'Meta': {'object_name': 'Quest'},
            'cmd_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'env': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'heroes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['heroes.Hero']", 'through': "orm['quests.QuestsHeroes']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'quests.questsheroes': {
            'Meta': {'object_name': 'QuestsHeroes'},
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['quests.Quest']"})
        },
        'roads.road': {
            'Meta': {'unique_together': "(('point_1', 'point_2'),)", 'object_name': 'Road'},
            'exists': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'point_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"}),
            'point_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"})
        }
    }

    complete_apps = ['actions']