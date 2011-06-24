# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MessagesLog'
        db.create_table('journal_messages_messageslog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hero', self.gf('django.db.models.fields.related.OneToOneField')(related_name='messages_log', unique=True, to=orm['heroes.Hero'])),
            ('messages', self.gf('django.db.models.fields.TextField')(default=u'[]')),
        ))
        db.send_create_signal('journal_messages', ['MessagesLog'])

        # Adding model 'MessagePattern'
        db.create_table('journal_messages_messagepattern', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('mask', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='proposed_journal_messages', to=orm['accounts.Account'])),
            ('editor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='edited_journal_messages', to=orm['accounts.Account'])),
            ('remove_after', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('journal_messages', ['MessagePattern'])


    def backwards(self, orm):
        
        # Deleting model 'MessagesLog'
        db.delete_table('journal_messages_messageslog')

        # Deleting model 'MessagePattern'
        db.delete_table('journal_messages_messagepattern')


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
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'actions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'heroes'", 'symmetrical': 'False', 'to': "orm['actions.Action']"}),
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
        'journal_messages.messagepattern': {
            'Meta': {'object_name': 'MessagePattern'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proposed_journal_messages'", 'to': "orm['accounts.Account']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'edited_journal_messages'", 'to': "orm['accounts.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mask': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'remove_after': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'journal_messages.messageslog': {
            'Meta': {'object_name': 'MessagesLog'},
            'hero': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'messages_log'", 'unique': 'True', 'to': "orm['heroes.Hero']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messages': ('django.db.models.fields.TextField', [], {'default': "u'[]'"})
        }
    }

    complete_apps = ['journal_messages']
