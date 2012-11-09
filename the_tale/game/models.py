# coding: utf-8

from django.db import models

from common.utils.enum import create_enum


class BUNDLE_TYPE:
    BASIC = 0

BUNDLE_TYPE_CHOICES = ( (BUNDLE_TYPE.BASIC, u'базовый'), )


class Bundle(models.Model):

    type =  models.IntegerField(null=False, choices=BUNDLE_TYPE_CHOICES)

    owner = models.CharField(null=True, max_length=32)


class BundleMember(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, related_name='+', unique=True)
    bundle = models.ForeignKey(Bundle, null=False, related_name='members')



SUPERVISOR_TASK_TYPE = create_enum('SUPERVISOR_TASK_TYPE', (('ARENA_PVP_1X1', 0, u'создать pvp бой на арене'),
                                                            ) )

SUPERVISOR_TASK_STATE = create_enum('SUPERVISOR_TASK_STATE', (('WAITING', 0, u'ожидает ресурсы'),
                                                              ('PROCESSED', 0, u'обработана'),
                                                              ('ERROR', 0, u'ошибка при обработке'),
                                                              ) )


class SupervisorTask(models.Model):

    type = models.IntegerField(null=False, choices=SUPERVISOR_TASK_TYPE.CHOICES)

    state = models.IntegerField(null=False, choices=SUPERVISOR_TASK_STATE.CHOICES, default=SUPERVISOR_TASK_STATE.WAITING)

    created_at = models.DateTimeField(auto_now_add=True, null=False)


class SupervisorTaskMember(models.Model):

    task = models.ForeignKey(SupervisorTask, null=False, related_name='+')

    account = models.ForeignKey('accounts.Account', null=False, related_name='+')
