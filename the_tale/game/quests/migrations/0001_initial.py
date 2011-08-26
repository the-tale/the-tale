# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Quest'
        db.create_table('quests_quest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('state', self.gf('django.db.models.fields.CharField')(default='uninitialized', max_length=50)),
            ('percents', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('quests', ['Quest'])

        # Adding model 'QuestMailDelivery'
        db.create_table('quests_questmaildelivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_quest', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mail_delivery', unique=True, to=orm['quests.Quest'])),
        ))
        db.send_create_signal('quests', ['QuestMailDelivery'])


    def backwards(self, orm):
        
        # Deleting model 'Quest'
        db.delete_table('quests_quest')

        # Deleting model 'QuestMailDelivery'
        db.delete_table('quests_questmaildelivery')


    models = {
        'quests.quest': {
            'Meta': {'object_name': 'Quest'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percents': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'uninitialized'", 'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'quests.questmaildelivery': {
            'Meta': {'object_name': 'QuestMailDelivery'},
            'base_quest': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mail_delivery'", 'unique': 'True', 'to': "orm['quests.Quest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['quests']
