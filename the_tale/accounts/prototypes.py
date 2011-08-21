# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from .models import Account

def get_account_by_id(model_id):
    angel = Account.objects.get(id=model_id)
    return AccountPrototype(model=angel)

def get_account_by_model(model):
    return AccountPrototype(model=model)

class AccountPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def user(self): return self.model.user

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): 
        self.model.save()

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {}

    @classmethod
    @nested_commit_on_success
    def create(cls, user):
        account_model = Account.objects.create(user=user)
        return AccountPrototype(model=account_model)

