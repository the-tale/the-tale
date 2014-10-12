# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = ( ("linguistics", "0016_save_not_moderated_phrase_candidates"),
                   ('heroes', "0120_auto__del_field_hero_name_forms"),
                   ('persons', '0019_auto__del_field_person_name_forms'),
                   ('places', '0040_auto__del_field_place_name_forms__del_field_building_name_forms'),
                   ('mobs', '0018_auto__del_field_mobrecord_name_forms'),
                   ('artifacts', '0019_auto__del_field_artifactrecord_name_forms'),
                   ('bills', '0029_textgen_to_utg') )

    def forwards(self, orm):
        # Deleting model 'PhraseCandidate'
        db.delete_table(u'phrase_candidates_phrasecandidate')


    def backwards(self, orm):
        # Adding model 'PhraseCandidate'
        db.create_table(u'phrase_candidates_phrasecandidate', (
            ('text', self.gf('django.db.models.fields.TextField')(max_length=10240, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('moderator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, on_delete=models.SET_NULL, to=orm['accounts.Account'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subtype_name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=256)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['accounts.Account'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type_name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=256)),
            ('subtype', self.gf('django.db.models.fields.CharField')(default=u'', max_length=256)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'phrase_candidates', ['PhraseCandidate'])


    models = {

    }

    complete_apps = ['phrase_candidates']
