# coding: utf-8
import datetime

from django.db import models
from django.contrib.auth.models import User

from common.utils.enum import create_enum


class Account(models.Model):

    MAX_NICK_LENGTH = 128

    user = models.OneToOneField(User, unique=True, null=False)

    nick = models.CharField(null=False, default=u'', max_length=MAX_NICK_LENGTH, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, default=datetime.datetime.fromtimestamp(0))

    updated_at = models.DateTimeField(auto_now=True, db_index=True, default=datetime.datetime.fromtimestamp(0))

    is_fast = models.BooleanField(default=True, db_index=True)

    # duplicate django user email - add unique constraints
    email = models.EmailField(max_length=254, null=True, unique=True)

    new_messages_number = models.IntegerField(null=False, default=0)

    class Meta:
        ordering = ['nick']

    def __unicode__(self): return self.nick


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

    type = models.IntegerField(choices=AWARD_TYPE.CHOICES, null=False)

    description = models.TextField(default='', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


class REGISTRATION_TASK_STATE:
    WAITING = 0
    PROCESSED = 1
    UNPROCESSED = 2
    ERROR = 3

REGISTRATION_TASK_STATE_CHOICES = ( (REGISTRATION_TASK_STATE.WAITING, u'ожидает обработки'),
                                    (REGISTRATION_TASK_STATE.PROCESSED, u'обработкана'),
                                    (REGISTRATION_TASK_STATE.UNPROCESSED, u'не обработана'),
                                    (REGISTRATION_TASK_STATE.ERROR, u'ошибка'),)

class RegistrationTask(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    state = models.IntegerField(default=REGISTRATION_TASK_STATE.WAITING, db_index=True, choices=REGISTRATION_TASK_STATE_CHOICES)

    comment = models.CharField(max_length=256, blank=True, null=True, default='')

    account = models.ForeignKey(Account,  related_name='+', null=True, default=None)


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
