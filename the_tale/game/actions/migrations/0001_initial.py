# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Action'
        db.create_table('actions_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('percents', self.gf('django.db.models.fields.FloatField')()),
            ('state', self.gf('django.db.models.fields.CharField')(default='uninitialized', max_length=50)),
            ('entropy', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('actions', ['Action'])

        # Adding model 'ActionIdleness'
        db.create_table('actions_actionidleness', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_action', self.gf('django.db.models.fields.related.OneToOneField')(related_name='action_idleness', unique=True, to=orm['actions.Action'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['heroes.Hero'])),
            ('entropy_action', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['actions.Action'])),
        ))
        db.send_create_signal('actions', ['ActionIdleness'])

        # Adding model 'ActionQuestMailDelivery'
        db.create_table('actions_actionquestmaildelivery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_action', self.gf('django.db.models.fields.related.OneToOneField')(related_name='action_quest', unique=True, to=orm['actions.Action'])),
            ('action_move_to_delivery_from', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['actions.Action'])),
            ('action_move_to_delivery_to', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['actions.Action'])),
        ))
        db.send_create_signal('actions', ['ActionQuestMailDelivery'])

        # Adding model 'ActionMoveTo'
        db.create_table('actions_actionmoveto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_action', self.gf('django.db.models.fields.related.OneToOneField')(related_name='action_move_to', unique=True, to=orm['actions.Action'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['heroes.Hero'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['places.Place'])),
            ('road', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['roads.Road'])),
            ('entropy_action', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='+', null=True, to=orm['actions.Action'])),
        ))
        db.send_create_signal('actions', ['ActionMoveTo'])

        # Adding model 'ActionBattlePvE_1x1'
        db.create_table('actions_actionbattlepve_1x1', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_action', self.gf('django.db.models.fields.related.OneToOneField')(related_name='action_battle_pve_1x1', unique=True, to=orm['actions.Action'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['heroes.Hero'])),
            ('npc', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['heroes.Hero'])),
            ('hero_initiative', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('npc_initiative', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal('actions', ['ActionBattlePvE_1x1'])

        # Adding model 'ActionResurrect'
        db.create_table('actions_actionresurrect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_action', self.gf('django.db.models.fields.related.OneToOneField')(related_name='action_resurrect', unique=True, to=orm['actions.Action'])),
            ('hero', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['heroes.Hero'])),
        ))
        db.send_create_signal('actions', ['ActionResurrect'])


    def backwards(self, orm):
        
        # Deleting model 'Action'
        db.delete_table('actions_action')

        # Deleting model 'ActionIdleness'
        db.delete_table('actions_actionidleness')

        # Deleting model 'ActionQuestMailDelivery'
        db.delete_table('actions_actionquestmaildelivery')

        # Deleting model 'ActionMoveTo'
        db.delete_table('actions_actionmoveto')

        # Deleting model 'ActionBattlePvE_1x1'
        db.delete_table('actions_actionbattlepve_1x1')

        # Deleting model 'ActionResurrect'
        db.delete_table('actions_actionresurrect')


    models = {
        'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'actions.action': {
            'Meta': {'object_name': 'Action'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entropy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percents': ('django.db.models.fields.FloatField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'uninitialized'", 'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'actions.actionbattlepve_1x1': {
            'Meta': {'object_name': 'ActionBattlePvE_1x1'},
            'base_action': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'action_battle_pve_1x1'", 'unique': 'True', 'to': "orm['actions.Action']"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'hero_initiative': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'npc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'npc_initiative': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'actions.actionidleness': {
            'Meta': {'object_name': 'ActionIdleness'},
            'base_action': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'action_idleness'", 'unique': 'True', 'to': "orm['actions.Action']"}),
            'entropy_action': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'actions.actionmoveto': {
            'Meta': {'object_name': 'ActionMoveTo'},
            'base_action': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'action_move_to'", 'unique': 'True', 'to': "orm['actions.Action']"}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"}),
            'entropy_action': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'road': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['roads.Road']"})
        },
        'actions.actionquestmaildelivery': {
            'Meta': {'object_name': 'ActionQuestMailDelivery'},
            'action_move_to_delivery_from': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'action_move_to_delivery_to': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'to': "orm['actions.Action']"}),
            'base_action': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'action_quest'", 'unique': 'True', 'to': "orm['actions.Action']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'actions.actionresurrect': {
            'Meta': {'object_name': 'ActionResurrect'},
            'base_action': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'action_resurrect'", 'unique': 'True', 'to': "orm['actions.Action']"}),
            'hero': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'angel': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'heroes'", 'null': 'True', 'blank': 'True', 'to': "orm['angels.Angel']"}),
            'chaoticity': ('django.db.models.fields.IntegerField', [], {}),
            'constitution': ('django.db.models.fields.IntegerField', [], {}),
            'first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'health': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intellect': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'npc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'roads.road': {
            'Meta': {'unique_together': "(('point_1', 'point_2'),)", 'object_name': 'Road'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'point_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"}),
            'point_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['places.Place']"})
        }
    }

    complete_apps = ['actions']
