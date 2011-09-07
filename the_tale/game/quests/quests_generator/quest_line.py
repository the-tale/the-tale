# coding: utf-8

from .environment import LocalEnvironment

class QuestLine(object):

    def __init__(self, env, place_start=None, person_start=None, place_end=None, person_end=None):
        self.env = LocalEnvironment()

        self.env.register('place_start', place_start if place_start else env.new_place())
        self.env.register('person_start', person_start if person_start else env.new_person())
        self.env.register('place_end', place_end if place_end else env.new_place())
        self.env.register('person_end', person_end if person_end else env.new_person())

    def create_line(self, env):
        self.line = []

    def get_description(self):
        description = [self.__class__.__name__]
        description.extend( [cmd.get_description() for cmd in self.line] )
        return description
