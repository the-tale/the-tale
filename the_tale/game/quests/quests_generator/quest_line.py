# coding: utf-8
from . import QuestGeneratorException
from .environment import LocalEnvironment
from .commands import deserialize_command

class QuestLine(object):

    def __init__(self):
        self.env_local = None
        self.id = None

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        self.id = identifier
        self.env_local = LocalEnvironment()

        if not place_start:
            place_start = env.new_place()

        if not person_start:
            person_start = env.new_person(from_place=place_start)

        if not place_end:
            place_end = env.new_place()

        if not person_end:
            person_end = env.new_person(from_place=place_end)

        self.env_local.register('place_start', place_start)
        self.env_local.register('person_start', person_start)
        self.env_local.register('place_end', place_end)
        self.env_local.register('person_end', person_end)

    @classmethod
    def type(cls): return cls.__name__.lower()

    def create_line(self, env):
        self.line = []

    def get_pointer_data(self, env, pointer):
        if pointer[0] >= len(self.line):
            return { 'cmd': None,
                     'quest': None }

        cmd = self.line[pointer[0]]

        if len(pointer) != 1:
            if not hasattr(cmd, 'quest'):
                raise QuestGeneratorException('command has no attribute "quest", cmd is: %r' % cmd.serialize())
            quest_line = env.quests[cmd.quest]
            return quest_line.get_pointer_data(env, pointer[1:])

        return { 'cmd': cmd,
                 'quest': self }

    def get_command(self, env, pointer):
        return self.get_pointer_data(env, pointer)['cmd']

    def get_quest(self, env, pointer):
        return self.get_pointer_data(env, pointer)['quest']

    def get_commands_number(self, env, pointer=None):

        if pointer is None:
            cmd_number = len(self.line)
            number = len(self.line)
        else:
            cmd_number = pointer[0]
            number = pointer[0]
        
        for cmd in self.line[:cmd_number]:
            if hasattr(cmd, 'quest'):
                number += env.quests[cmd.quest].get_commands_number(env)
                
        if pointer and len(pointer) > 1:
            cmd = self.line[cmd_number]
            if not hasattr(cmd, 'quest'):
                raise QuestGeneratorException('command has no attribute "quest", cmd is: %r' % cmd.serialize())
            number += 1 + env.quests[cmd.quest].get_commands_number(env, pointer[1:])

        return number

    def get_percents(self, env, pointer):
        return float(self.get_commands_number(env, pointer)) / self.get_commands_number(env)

    def get_start_pointer(self):
        return [0]

    def increment_pointer(self, env, pointer):

        cmd = self.line[pointer[0]]

        if len(pointer) == 1:
            if hasattr(cmd, 'quest'):
                return [pointer[0]] + self.get_start_pointer()
            if len(self.line) > pointer[0]+1:
                return [pointer[0]+1]
            return None

        next_subpointer = env.quests[self.line[pointer[0]].quest].increment_pointer(env, pointer[1:])
        
        if next_subpointer is None:
            if len(self.line) > pointer[0]+1:
                return [pointer[0]+1]
            return None

        next_pointer = [pointer[0]]
        next_pointer.extend(next_subpointer)

        return next_pointer

    def get_quest_action_chain(self, env, pointer):
        cmd = self.line[pointer[0]]
        chain = [ (self, cmd ) ]

        if len(pointer) == 1:
            return chain

        if not hasattr(cmd, 'quest'):
            raise QuestGeneratorException('command has no attribute "quest", cmd is: %r' % cmd.serialize())

        quest_line = env.quests[cmd.quest]

        chain.extend( quest_line.get_quest_action_chain(env, pointer[1:]) )

        return chain


    def get_description(self):
        description = [self.__class__.__name__]
        description.extend( [cmd.get_description() for cmd in self.line] )
        return description

    def serialize(self):
        return { 'type': self.type(),
                 'id': self.id,
                 'line': [cmd.serialize() for cmd in self.line],
                 'env_local': self.env_local.serialize() }

    def deserialize(self, data):
        self.id = data['id']

        self.line = []

        for cmd_data in data['line']:
            self.line.append(deserialize_command(cmd_data))

        self.env_local = LocalEnvironment()
        self.env_local.deserialize(data['env_local'])
