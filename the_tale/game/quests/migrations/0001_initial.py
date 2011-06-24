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
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('quests', ['Quest'])

        # Adding model 'QuestMailDelivery'
        db.create_table('quests_questmaildelivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_quest', self.gf('django.db.models.fields.related.OneToOneField')(related_name='quest_mail_delivery', unique=True, to=orm['quests.Quest'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['heroes.Hero'])),
            ('delivery_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='quests_mail_delivery_from', to=orm['places.Place'])),
            ('delivery_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='quests_mail_delivery_to', to=orm['places.Place'])),
            ('action_delivery_from', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['actions.Action'])),
            ('action_delivery', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['actions.Action'])),
        ))
        db.send_create_signal('quests', ['QuestMailDelivery'])


    def backwards(self, orm):
        
        # Deleting model 'Quest'
        db.delete_table('quests_quest')

        # Deleting model 'QuestMailDelivery'
        db.delete_table('quests_questmaildelivery')


    models = {
        'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'actions.action': {
            'Meta': {'object_name': 'Action'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percents': ('django.db.models.fields.FloatField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'angels.angel': {
            'Meta': {'object_name': 'Angel'},
            'account': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['accounts.Account']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
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
        'heroes.hero': {
            'Meta': {'object_name': 'Hero'},
            'actions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'heroes'", 'symmetrical': 'False', 'through': "orm['heroes.HeroAction']", 'to': "orm['actions.Action']"}),
            'angel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'heroes'", 'to': "orm['angels.Angel']"}),
            'chaoticity': ('django.db.models.fields.IntegerField', [], {}),
            'constitution': ('django.db.models.fields.IntegerField', [], {}),
            'first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'folly_energy': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intellect': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'reflexes': ('django.db.models.fields.IntegerField', [], {}),
            'wisdom': ('django.db.models.fields.IntegerField', [], {})
        },
        'heroes.heroaction': {
            'Meta': {'object_name': 'HeroAction'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['actions.Action']"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'places.place': {
            'Meta': {'object_name': 'Place'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'x': ('django.db.models.fields.BigIntegerField', [], {}),
            'y': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'quests.quest': {
            'Meta': {'object_name': 'Quest'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'quests.questmaildelivery': {
            'Meta': {'object_name': 'QuestMailDelivery'},
            'action_delivery': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'action_delivery_from': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'base_quest': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'quest_mail_delivery'", 'unique': 'True', 'to': "orm['quests.Quest']"}),
            'delivery_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quests_mail_delivery_from'", 'to': "orm['places.Place']"}),
            'delivery_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quests_mail_delivery_to'", 'to': "orm['places.Place']"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['quests']
