# -*- coding: utf-8 -*-
import datetime
import json
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("heroes", "0068_auto__del_field_hero_actions_descriptions__del_field_hero_last_action_"),
    )

    def forwards(self, orm):

        for hero in orm['heroes.Hero'].objects.all():
            actions_data = json.loads(hero.actions)

            for action_model, action in zip(orm['actions.Action'].objects.filter(hero_id=hero.id).order_by('order'), actions_data['actions']):
                action.update({ 'type': action_model.type,
                                'bundle_id': action_model.bundle_id,
                                'state': action_model.state,
                                'percents': action_model.percents,
                                'created_at_turn': action_model.created_at_turn,
                                'context': json.loads(action_model.context),
                                'mob': json.loads(action_model.mob),
                                'data': json.loads(action_model.data),
                                'mob_context': json.loads(action_model.mob_context),
                                'quest_id': action_model.quest_id,
                                'place_id': action_model.place_id,
                                'break_at': action_model.break_at,
                                'length': action_model.length,
                                'destination_x': action_model.destination_x,
                                'destination_y': action_model.destination_y,
                                'percents_barier': action_model.percents_barier,
                                'extra_probability': action_model.extra_probability,
                                'textgen_id': action_model.textgen_id,
                                'hero_health_lost': action_model.hero_health_lost,
                                'back': action_model.back,
                                'meta_action_id': action_model.meta_action_id })

            hero.actions = json.dumps(actions_data)
            hero.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'actions.action': {
            'Meta': {'object_name': 'Action'},
            'back': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'break_at': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Bundle']"}),
            'context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'destination_x': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'destination_y': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'extra_probability': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['heroes.Hero']"}),
            'hero_health_lost': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'meta_action': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['actions.MetaAction']", 'null': 'True'}),
            'mob': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'mob_context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['actions.Action']"}),
            'percents': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'percents_barier': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['places.Place']"}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['quests.Quest']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'uninitialized'", 'max_length': '50'}),
            'textgen_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'actions.metaaction': {
            'Meta': {'object_name': 'MetaAction'},
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['game.Bundle']", 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percents': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'uninitialized'", 'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'actions.metaactionmember': {
            'Meta': {'object_name': 'MetaActionMember'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['actions.MetaAction']"}),
            'context': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['heroes.Hero']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '32'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'game.bundle': {
            'Meta': {'object_name': 'Bundle'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'abilities': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'account': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'heroes'", 'null': 'True', 'blank': 'True', 'to': u"orm['accounts.Account']"}),
            'actions': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'active_state_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'bag': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'ban_state_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'destiny_points_spend': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'diary': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'energy': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'equipment': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'experience': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'health': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_alive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_fast': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'last_energy_regeneration_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'messages': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'might': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'might_updated_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'money': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'next_spending': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'places_history': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'pos_from_x': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_from_y': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_invert_direction': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'pos_percents': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_place': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['places.Place']"}),
            'pos_road': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['roads.Road']"}),
            'pos_to_x': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pos_to_y': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pref_enemy': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['persons.Person']"}),
            'pref_enemy_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_energy_regeneration_type': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'pref_energy_regeneration_type_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_equipment_slot': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'pref_equipment_slot_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_friend': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['persons.Person']"}),
            'pref_friend_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_mob': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['mobs.MobRecord']", 'null': 'True', 'blank': 'True'}),
            'pref_mob_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'pref_place': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['places.Place']"}),
            'pref_place_changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'premium_state_end_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'pvp': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
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
            'stat_pvp_battles_1x1_draws': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_pvp_battles_1x1_number': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_pvp_battles_1x1_victories': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'stat_quests_done': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'ui_caching_started_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'mobs.mobrecord': {
            'Meta': {'object_name': 'MobRecord'},
            'abilities': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['accounts.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'terrains': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'persons.person': {
            'Meta': {'object_name': 'Person'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'enemies_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'friends_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'out_game_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'persons'", 'to': u"orm['places.Place']"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('rels.django.TableIntegerField', [], {})
        },
        u'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'race': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'updated_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'quests.quest': {
            'Meta': {'object_name': 'Quest'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'env': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'heroes': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['heroes.Hero']", 'through': u"orm['quests.QuestsHeroes']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'quests.questsheroes': {
            'Meta': {'object_name': 'QuestsHeroes'},
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['heroes.Hero']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['quests.Quest']"})
        },
        u'roads.road': {
            'Meta': {'unique_together': "(('point_1', 'point_2'),)", 'object_name': 'Road'},
            'exists': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'point_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['places.Place']"}),
            'point_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['places.Place']"})
        }
    }

    complete_apps = ['actions']
    symmetrical = True
