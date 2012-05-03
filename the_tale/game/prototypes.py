# coding: utf-8
from .models import Time

def get_current_time():
    try:
        return TimePrototype(model=Time.objects.all()[0])
    except IndexError:
        return TimePrototype.create()

class TimePrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def turn_number(self): return self.model.turn_number

    def increment_turn(self):
        self.model.turn_number += 1

    def save(self):
        self.model.save()

    @classmethod
    def create(cls):
        return cls(model=Time.objects.create())

    def ui_info(self):
        return { 'number': self.turn_number }
