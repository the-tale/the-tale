# coding: utf-8
import random

from .environment import LocalEnvironment

class QuestLine(object):

    def __init__(self, env, place_start=None, person_start=None, place_end=None, person_end=None):
        self.env = LocalEnvironment()
        self.writer = None

        self.env.register('place_start', place_start if place_start else env.new_place())
        self.env.register('person_start', person_start if person_start else env.new_person())
        self.env.register('place_end', place_end if place_end else env.new_place())
        self.env.register('person_end', person_end if person_end else env.new_person())

    @classmethod
    def type_name(cls): return cls.__name__.lower()

    def create_line(self, env):
        self.line = []

    def get_description(self):
        description = [self.__class__.__name__]
        description.extend( [cmd.get_description() for cmd in self.line] )
        return description

    def set_writer(self, writers):
        writer = random.choice(writers[self.type_name()])
        self.writer = writer.get_type_name()
        for cmd in self.line:
            cmd.set_writer(writers)

    def get_sequence_len(self):
        return reduce(lambda s, el: s + el.get_sequence_len(), self.line, 0)

    def get_json(self):

        return { 'name': self.__class__.__name__,
                 'line': [ cmd.get_json() for cmd in self.line],
                 'writer': self.writer,
                 'env': self.env.save_to_dict(),
                 'sequence_len': self.get_sequence_len()
            }
