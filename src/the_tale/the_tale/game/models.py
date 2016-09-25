# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game import relations


class SupervisorTask(models.Model):
    type = RelationIntegerField(relation=relations.SUPERVISOR_TASK_TYPE)
    state = RelationIntegerField(relation=relations.SUPERVISOR_TASK_STATE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)


class SupervisorTaskMember(models.Model):
    task = models.ForeignKey(SupervisorTask, null=False, related_name='+', on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.PROTECT)
