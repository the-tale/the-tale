# coding: utf-8
import datetime

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from rels.django_staff import TableIntegerField

from accounts.relations import AWARD_TYPE


class AccountManager(BaseUserManager):

    @classmethod
    def normalize_email(cls, email):
        email = super(AccountManager, cls).normalize_email(email)
        return email if email else None

    def create_user(self, nick, email, is_fast=None, password=None):

        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email),
                             nick=nick,
                             is_fast=is_fast)
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

    nick = models.CharField(null=False, default=u'', max_length=MAX_NICK_LENGTH, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, default=datetime.datetime.fromtimestamp(0))

    updated_at = models.DateTimeField(auto_now=True, db_index=True, default=datetime.datetime.fromtimestamp(0))

    is_fast = models.BooleanField(default=True, db_index=True)

    # duplicate django user email - add unique constraints
    email = models.EmailField(max_length=254, null=True, unique=True, blank=True)

    new_messages_number = models.IntegerField(null=False, default=0)

    last_news_remind_time = models.DateTimeField(auto_now_add=True, default=datetime.datetime.fromtimestamp(0))

    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))

    USERNAME_FIELD = 'nick'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['nick']
        permissions = (("moderate_account", u"Может редактировать аккаунты и т.п."), )

    def __unicode__(self): return self.nick

    def get_full_name(self): return self.nick

    def get_short_name(self): return self.nick


class Award(models.Model):

    account = models.ForeignKey(Account,  related_name='+', null=False)

    type = TableIntegerField(relation=AWARD_TYPE, relation_column='value', db_index=True)

    description = models.TextField(default='', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)



class CHANGE_CREDENTIALS_TASK_STATE:
    WAITING = 0
    EMAIL_SENT = 1
    PROCESSED = 2
    UNPROCESSED = 3
    ERROR = 4
    TIMEOUT = 5

CHANGE_CREDENTIALS_TASK_STATE_CHOICES = ( (CHANGE_CREDENTIALS_TASK_STATE.WAITING, u'ожидает обработки'),
                                          (CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT, u'отослано письмо'),
                                          (CHANGE_CREDENTIALS_TASK_STATE.PROCESSED, u'обработана'),
                                          (CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED, u'не обработана'),
                                          (CHANGE_CREDENTIALS_TASK_STATE.ERROR, u'ошибка'),
                                          (CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT, u'таймаут') )


class ChangeCredentialsTask(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    state = models.IntegerField(default=CHANGE_CREDENTIALS_TASK_STATE.WAITING, db_index=True, choices=CHANGE_CREDENTIALS_TASK_STATE_CHOICES)

    comment = models.CharField(max_length=256, blank=True, null=True, default='')

    account = models.ForeignKey(Account,  related_name='+')

    old_email = models.EmailField(max_length=254, null=True)

    new_email = models.EmailField(max_length=254, null=True)

    new_password = models.TextField(default=None, null=True) # django password hash

    new_nick = models.CharField(default=None, null=True, max_length=30)

    uuid = models.CharField(max_length=32, db_index=True)
