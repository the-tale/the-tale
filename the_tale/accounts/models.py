# coding: utf-8
import datetime

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from rels.django import TableIntegerField

from the_tale.accounts.relations import AWARD_TYPE, CHANGE_CREDENTIALS_TASK_STATE


class AccountManager(BaseUserManager):

    @classmethod
    def normalize_email(cls, email):
        email = super(AccountManager, cls).normalize_email(email)
        return email if email else None

    def create_user(self, nick, email, is_fast=None, password=None, active_end_at=None, referer=None, referer_domain=None, referral_of=None, is_bot=False):

        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email),
                             nick=nick,
                             is_fast=is_fast,
                             active_end_at=active_end_at,
                             referer=referer,
                             referer_domain=referer_domain,
                             is_bot=is_bot,
                             referral_of=referral_of)
        account.set_password(password)
        account.save(using=self._db)
        return account

    def create_superuser(self, nick, email, password):
        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email),
                             nick=nick,
                             is_fast=False,
                             is_superuser=True,
                             is_staff=True)
        account.set_password(password)
        account.save(using=self._db)
        return account


class Account(AbstractBaseUser, PermissionsMixin):

    objects = AccountManager()

    MAX_NICK_LENGTH = 128
    MAX_EMAIL_LENGTH = 254

    nick = models.CharField(null=False, default=u'', max_length=MAX_NICK_LENGTH, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, default=datetime.datetime.fromtimestamp(0))

    updated_at = models.DateTimeField(auto_now=True, db_index=True, default=datetime.datetime.fromtimestamp(0))

    premium_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    active_end_at = models.DateTimeField(db_index=True)

    premium_expired_notification_send_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    is_fast = models.BooleanField(default=True, db_index=True)
    is_bot = models.BooleanField(default=False)

    # duplicate django user email - add unique constraints
    email = models.EmailField(max_length=MAX_EMAIL_LENGTH, null=True, unique=True, blank=True)

    new_messages_number = models.IntegerField(null=False, default=0)

    last_news_remind_time = models.DateTimeField(auto_now_add=True, default=datetime.datetime.fromtimestamp(0))

    clan = models.ForeignKey('clans.Clan', null=True, default=None, related_name='+', on_delete=models.SET_NULL)

    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))

    personal_messages_subscription = models.BooleanField(blank=True, default=True)

    ban_game_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    ban_forum_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    referer_domain = models.CharField(max_length=256, null=True, default=None, db_index=True)
    referer = models.CharField(max_length=4*1024, null=True, default=None)

    referral_of = models.ForeignKey('accounts.Account', null=True, blank=True, db_index=True, default=None, on_delete=models.SET_NULL)
    referrals_number = models.IntegerField(default=0)

    permanent_purchases = models.TextField(default='[]')

    might = models.FloatField(default=0.0)

    USERNAME_FIELD = 'nick'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['nick']
        permissions = (("moderate_account", u"Может редактировать аккаунты и т.п."), )

    def __unicode__(self): return self.nick

    def get_full_name(self): return self.nick

    def get_short_name(self): return self.nick


class Award(models.Model):

    account = models.ForeignKey(Account,  related_name='+', null=False, on_delete=models.CASCADE)

    type = TableIntegerField(relation=AWARD_TYPE, relation_column='value', db_index=True)

    description = models.TextField(default='', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


class ResetPasswordTask(models.Model):
    account = models.ForeignKey(Account,  related_name='+', null=False, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False, db_index=True)

class ChangeCredentialsTask(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    state = TableIntegerField(relation=CHANGE_CREDENTIALS_TASK_STATE, relation_column='value', db_index=True)

    comment = models.CharField(max_length=256, blank=True, null=True, default='')

    account = models.ForeignKey(Account,  related_name='+', on_delete=models.CASCADE)

    old_email = models.EmailField(max_length=254, null=True)

    new_email = models.EmailField(max_length=254, null=True)

    new_password = models.TextField(default=None, null=True) # django password hash

    new_nick = models.CharField(default=None, null=True, max_length=Account.MAX_NICK_LENGTH)

    uuid = models.CharField(max_length=32, db_index=True)

    relogin_required = models.BooleanField(blank=True, default=False)
