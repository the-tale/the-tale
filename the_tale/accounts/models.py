# coding: utf-8
import datetime

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from common.utils.enum import create_enum


class AccountManager(BaseUserManager):

    def create_user(self, nick, email, is_fast=None, password=None):

        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email) if email is not None else None,
                             nick=nick,
                             is_fast=is_fast)
        account.set_password(password)
        account.save(using=self._db)
        return account

    def create_superuser(self, nick, email, password):
        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email) if email is not None else None,
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
    email = models.EmailField(max_length=254, null=True, unique=True)

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


AWARD_TYPE = create_enum('AWARD_TYPE', (('BUG_MINOR', 0, u'найдена ошибка: небольшая'),
                                        ('BUG_NORMAL', 1, u'найдена ошибка: обычная'),
                                        ('BUG_MAJOR', 2, u'найдена ошибка: существенная'),
                                        ('CONTEST_1_PLACE', 3, u'конкурс: 1-ое место'),
                                        ('CONTEST_2_PLACE', 4, u'конкурс: 2-ое место'),
                                        ('CONTEST_3_PLACE', 5, u'конкурс: 3-е место'),
                                        ('STANDARD_MINOR', 6, u'стандартная награда: небольшая'),
                                        ('STANDARD_NORMAL', 7, u'стандартная награда: обычная'),
                                        ('STANDARD_MAJOR', 8, u'стандартная награда: существенная'),))

class Award(models.Model):

    account = models.ForeignKey(Account,  related_name='+', null=False)

    type = models.IntegerField(choices=AWARD_TYPE._CHOICES, null=False)

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
