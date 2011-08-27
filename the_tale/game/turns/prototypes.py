# -*- coding: utf-8 -*-

from django_next.utils.decorators import nested_commit_on_success

from .models import Turn

def get_turn_by_id(model_id):
    turn = Turn.objects.get(id=model_id)
    return TurnPrototype(model=turn)

def get_latest_turn():
    turn = Turn.objects.latest(field_name='id')
    return TurnPrototype(model=turn)

def get_turn_by_model(model):
    return TurnPrototype(model=model)


class TurnPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def number(self): return self.model.id

    def remove(self): return self.model.delete()
    def save(self): self.model.save(force_update=True)

    def ui_info(self):
        return {'number': self.number}


    @classmethod
    @nested_commit_on_success
    def create(cls):
        turn = Turn.objects.create()
        turn.save()
        return cls(model=turn)

