# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = ( ('heroes', '0088_reset_actions'), )

    def forwards(self, orm):
        # Removing unique constraint on 'QuestChoice', fields ['quest', 'choice_point']
        db.delete_unique(u'quests_questchoice', ['quest_id', 'choice_point'])

        # Deleting model 'Quest'
        db.delete_table(u'quests_quest')

        # Deleting model 'QuestsHeroes'
        db.delete_table(u'quests_questsheroes')

        # Deleting model 'QuestChoice'
        db.delete_table(u'quests_questchoice')


    def backwards(self, orm):
        # Adding model 'Quest'
        db.create_table(u'quests_quest', (
            ('created_at_turn', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('env', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('data', self.gf('django.db.models.fields.TextField')(default='{}')),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'quests', ['Quest'])

        # Adding model 'QuestsHeroes'
        db.create_table(u'quests_questsheroes', (
            ('quest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['quests.Quest'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['heroes.Hero'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'quests', ['QuestsHeroes'])

        # Adding model 'QuestChoice'
        db.create_table(u'quests_questchoice', (
            ('quest', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choices', to=orm['quests.Quest'])),
            ('choice_point', self.gf('django.db.models.fields.CharField')(max_length=32)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'quests', ['QuestChoice'])

        # Adding unique constraint on 'QuestChoice', fields ['quest', 'choice_point']
        db.create_unique(u'quests_questchoice', ['quest_id', 'choice_point'])


    models = {

    }

    complete_apps = ['quests']
