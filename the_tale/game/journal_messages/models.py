from django.db import models

from game.heroes.models import Hero
from accounts.models import Account

class MessagesLog(models.Model):

    hero = models.OneToOneField(Hero, related_name='messages_log')

    messages = models.TextField(default=u'[]')


##########################
# live cycle:
# approved <=> unapproved <=> remove_query
##########################

class MessagePattern(models.Model):

    class STATE:
        APPROVED = 1
        UNAPPROVED = 2
        REMOVED = 3

    STATE_CHOICES = ( (STATE.APPROVED, 'APPROVED'),
                      (STATE.UNAPPROVED, 'UNAPPROVED'),
                      (STATE.REMOVED, 'REMOVED'))

    created_at = models.DateTimeField(auto_now_add=True)

    state = models.IntegerField(null=False, default=STATE.UNAPPROVED, choices=STATE_CHOICES)
    
    type = models.CharField(null=False, max_length=50)

    mask = models.BigIntegerField(default=0)

    text = models.TextField()

    comment = models.TextField()

    author = models.ForeignKey(Account, related_name='proposed_journal_messages', null=True, default=None, on_delete=models.SET_NULL)
    editor = models.ForeignKey(Account, related_name='edited_journal_messages', null=True, default=None, on_delete=models.SET_NULL)

    remove_after = models.DateTimeField(null=True)

