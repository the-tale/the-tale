# coding: utf-8

class Writer(object):

    QUEST_TYPE = None

    ACTIONS = {}
    LOG = {}
    CHOICES = {}

    def __init__(self, env, local_env):
        self.subst = env.get_msg_substitutions(local_env)
    
    @classmethod
    def type(cls):
        return cls.__name__.lower()

    def get_action_msg(self, event):
        msg = self.ACTIONS.get(event)
        if msg:
            return msg % self.subst

    def get_log_msg(self, event):
        msg = self.LOG.get(event)
        if msg:
            return msg % self.subst

    def get_choice_msg(self, choice_id):
        data = self.CHOICES.get(choice_id)
        if data:
            return data['question'] % self.subst

    def get_choice_result_msg(self, choice_id, choice):
        data = self.CHOICES.get(choice_id)
        if data:
            return data['results'][choice] % self.subst


class Default(object):

    def get_action_msg(self, event):
        return None

    def get_log_msg(self, event):
        return None

