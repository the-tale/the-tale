# -*- coding: utf-8 -*-
import json

from the_tale.common.utils.constant_code.textgen_to_utg import convert_textgen_noun_json_to_utg

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    depends_on = ( ("linguistics", "0009_load_lexicon"), )

    def forwards(self, orm):

        for model in orm['persons.Person'].objects.all():
            textgen_data = json.loads(model.name_forms)
            person_data = json.loads(model.data)

            person_data['name'] = convert_textgen_noun_json_to_utg(textgen_data, aninality=True)

            model.data = json.dumps(person_data)
            model.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
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
        u'places.place': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Place'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'created_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'data': ('django.db.models.fields.TextField', [], {'default': "u'{}'"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'expected_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'freedom': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'goods': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'habit_honor': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'habit_honor_negative': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'habit_honor_positive': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'habit_peacefulness': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'habit_peacefulness_negative': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'habit_peacefulness_positive': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'heroes_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_frontier': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keepers_goods': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'modifier': ('rels.django.RelationIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'name_forms': ('django.db.models.fields.TextField', [], {'default': "u''"}),
            'persons_changed_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'production': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'race': ('rels.django.RelationIntegerField', [], {}),
            'safety': ('django.db.models.fields.FloatField', [], {'default': '0.75'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'stability': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'tax': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'transport': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_at_turn': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['persons']
    symmetrical = True
