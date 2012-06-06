# coding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):

     user = models.OneToOneField(User, unique=True, null=False)


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

    state = models.IntegerField(default=REGISTRATION_TASK_STATE.WAITING, db_index=True)

    comment = models.CharField(max_length=256, blank=True, null=True, default='')

    account = models.ForeignKey(Account,  related_name='+', null=True, default=None, db_index=True)
