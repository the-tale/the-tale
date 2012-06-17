# coding: utf-8
from game.quests.quests_generator.exceptions import QuestGeneratorException
from game.quests.quests_generator.environment import LocalEnvironment
from game.quests.quests_generator.commands import deserialize_command

class Line(object):

    def __init__(self, sequence=[]):
        self.sequence = sequence

    def get_start_pointer(self):
        return [0]

    def get_commands_number(self, env, pointer=None):

        if pointer is None:
            cmd_number = len(self.sequence)
            number = len(self.sequence)
        else:
            if pointer[0] >= len(self.sequence):
                raise QuestGeneratorException('get_commands_number: wrong pointer value (%r) for this line' % pointer)
            cmd_number = pointer[0]
            number = pointer[0]

        for cmd in self.sequence[:cmd_number]:
            if cmd.is_quest:
                number += env.quests[cmd.quest].get_commands_number(env)
            elif cmd.is_choice:
                number += max(env.lines[line].get_commands_number(env) for line in cmd.choices.values())

        if pointer and len(pointer) > 1:
            cmd = self.sequence[cmd_number]
            if cmd.is_quest:
                number += 1 + env.quests[cmd.quest].get_commands_number(env, pointer[1:])
            elif cmd.is_choice:
                number += 1 + env.lines[pointer[1]].get_commands_number(env, pointer[2:])
            else:
                raise QuestGeneratorException('command has no attribute "quest" or "choices", cmd is: %r' % cmd.serialize())

        return number

    def increment_pointer(self, env, pointer, choices):

        if pointer[0] >= len(self.sequence):
            raise QuestGeneratorException('increment pointer: wrong pointer value (%r) for this line' % pointer)

        cmd = self.sequence[pointer[0]]

        if len(pointer) == 1:
            if cmd.is_quest:
                return [pointer[0]] + self.get_start_pointer()
            if cmd.is_choice:
                choice = choices.get(cmd.id, cmd.default)
                choosed_line = cmd.choices[choice]
                return [pointer[0], choosed_line] + env.lines[choosed_line].get_start_pointer()
            if len(self.sequence) > pointer[0]+1:
                return [pointer[0]+1]
            return None

        if cmd.is_quest:
            prev_subpointer = pointer[0:1]
            next_subpointer = env.quests[self.sequence[pointer[0]].quest].increment_pointer(env, pointer[1:], choices)
        if cmd.is_choice:
            prev_subpointer = pointer[0:2]
            next_subpointer = env.lines[pointer[1]].increment_pointer(env, pointer[2:], choices)

        if next_subpointer is None:
            if len(self.sequence) > pointer[0]+1:
                return [pointer[0]+1]
            return None

        next_pointer = []
        next_pointer.extend(prev_subpointer)
        next_pointer.extend(next_subpointer)

        return next_pointer

    def get_quest_command(self, env, pointer, choices=None):
        '''
        return cmd, choices list, subpointer
        '''

        if choices is None:
            choices = []

        if pointer[0] >= len(self.sequence):
            raise QuestGeneratorException('get quest command: wrong pointer value (%r) for this line' % pointer)

        cmd = self.sequence[pointer[0]]

        if not cmd.is_choice:
            return cmd, choices, pointer[1:]

        if len(pointer) == 1:
            return cmd, choices, []

        if pointer[1] not in cmd.choices.values():
            raise QuestGeneratorException(u'wrong pointer "%r" - line "%s" not in choice "%s"' % (pointer, pointer[1], cmd.get_description(env)))

        choices.append((cmd.choice, cmd.get_choice_by_line(pointer[1])))
        return env.lines[pointer[1]].get_quest_command(env, pointer[2:], choices=choices)

    def serialize(self):
        return {'sequence': [cmd.serialize() for cmd in self.sequence]}

    def deserialize(self, data):
        self.sequence = [ deserialize_command(cmd_data) for cmd_data in data['sequence']]

    def get_description(self, env):
        return [cmd.get_description(env) for cmd in self.sequence]

    def __eq__(self, other):
        return self.sequence == other.sequence


class Quest(object):

    def __init__(self):
        self.env_local = None
        self.id = None
        self.line = None

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        self.id = identifier
        self.env_local = LocalEnvironment()

        if not place_start:
            if person_start:
                raise QuestGeneratorException(u'person "%s" specified without place' % person_start)
            place_start = env.new_place()

        if not person_start:
            person_start = env.new_person(from_place=place_start)

        if not place_end:
            if person_end:
                raise QuestGeneratorException(u'person "%s" specified without place' % person_end)
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
        raise NotImplementedError

    def get_command(self, env, pointer):
        return self.get_quest_action_chain(env, pointer)[-1][1]

    def get_quest(self, env, pointer):
        return self.get_quest_action_chain(env, pointer)[-1][0]

    def get_commands_number(self, env, pointer=None):
        return env.lines[self.line].get_commands_number(env=env, pointer=pointer)

    def get_percents(self, env, pointer):
        return float(self.get_commands_number(env, pointer)) / self.get_commands_number(env)

    def get_start_pointer(self, env):
        return env.lines[self.line].get_start_pointer()

    def increment_pointer(self, env, pointer, choices):
        return env.lines[self.line].increment_pointer(env, pointer, choices)

    def get_quest_action_chain(self, env, pointer):
        cmd, choices, subpointer = env.lines[self.line].get_quest_command(env, pointer)
        chain = [ (self, cmd, choices ) ]

        if not subpointer:
            return chain

        if not cmd.is_quest:
            raise QuestGeneratorException('command has no attribute "quest", cmd is: %r' % cmd.serialize())

        quest = env.quests[cmd.quest]

        chain.extend( quest.get_quest_action_chain(env, subpointer) )

        return chain

    def get_description(self, env):
        description = [self.__class__.__name__]
        description.extend( env.lines[self.line].get_description(env) )
        return description

    def serialize(self):
        return { 'type': self.type(),
                 'id': self.id,
                 'line': self.line,
                 'env_local': self.env_local.serialize() }

    def deserialize(self, data):
        self.id = data['id']
        self.line = data['line']

        self.env_local = LocalEnvironment()
        self.env_local.deserialize(data['env_local'])

    def __eq__(self, other):
        return (self.id == other.id and
                self.line == other.line and
                self.env_local == other.env_local)
