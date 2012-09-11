# coding: utf-8
import copy
import random

from game.quests.quests_generator.exceptions import QuestGeneratorException
from game.quests.quests_generator.environment import LocalEnvironment
from game.quests.quests_generator.commands import deserialize_command

class ACTOR_TYPE:
    PERSON = 0
    PLACE = 1

class Line(object):

    def __init__(self, sequence=[]):
        self.sequence = [element for element in sequence if element is not None]
        self.available = None

        # temporary storage for real power changes (such changes, that necessary be at that line)
        self._power_changes = {}

    def get_start_pointer(self):
        return [0]

    def calculate_power_changes(self, env, powers):
        powers = copy.copy(powers) + [cmd for cmd in reversed(self.sequence) if cmd.is_givepower]

        for cmd in self.sequence:
            if cmd.is_quest:
                env.quests[cmd.quest].calculate_power_changes(env, powers)
            elif cmd.is_choice:
                for line in cmd.choices.values():
                    env.lines[line].calculate_power_changes(env, powers)

        for cmd in reversed(powers):
            if cmd.depends_on is not None:
                if cmd.depends_on not in self._power_changes:
                    continue
                self._power_changes[cmd.person] = self._power_changes.get(cmd.person,0) + self._power_changes[cmd.depends_on] * cmd.multiply
            else:
                self._power_changes[cmd.person] = self._power_changes.get(cmd.person,0) + cmd.power


    def calculate_availability(self, env):
        friend_data = env.knowlege_base.get_special('hero_pref_friend')
        friend_uuid = friend_data['uuid'] if friend_data else None

        if friend_uuid and self._power_changes.get(friend_uuid, 0) < 0:
            self.available = False
            return False

        enemy_data = env.knowlege_base.get_special('hero_pref_enemy')
        enemy_uuid = enemy_data['uuid'] if enemy_data else None

        if enemy_uuid and self._power_changes.get(enemy_uuid, 0) > 0:
            self.available = False
            return False

        for cmd in self.sequence:
            if cmd.is_quest:
                if not env.quests[cmd.quest].calculate_availability(env):
                    self.available = False
                    return False
            elif cmd.is_choice:
                for line in cmd.choices.values():
                    env.lines[line].calculate_availability(env)
                if not any(env.lines[line].available for line in cmd.choices.values()):
                    self.available = False
                    return False

        self.available = True
        return True


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
                choice = choices.get(cmd.id, random.choice(cmd.get_variants()))
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
        return {'sequence': [cmd.serialize() for cmd in self.sequence],
                'available': self.available}

    def deserialize(self, data):
        self.sequence = [ deserialize_command(cmd_data) for cmd_data in data['sequence']]
        self.available = data.get('available', True)

    def get_description(self, env):
        return [cmd.get_description(env) for cmd in self.sequence]

    def __eq__(self, other):
        return self.sequence == other.sequence


class Quest(object):

    SPECIAL = False

    ACTORS = []
    CHOICES = {}

    def __init__(self):
        self.id = None
        self.line = None
        self.env_local = LocalEnvironment()
        self.available = None

    @classmethod
    def can_be_used(cls, env):
        return True

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        self.id = identifier

    @classmethod
    def type(cls): return cls.__name__.lower()

    def create_line(self, env):
        raise NotImplementedError

    def calculate_power_changes(self, env, powers):
        return env.lines[self.line].calculate_power_changes(env, powers)

    def calculate_availability(self, env):
        self.available = env.lines[self.line].calculate_availability(env)
        return self.available

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

    def get_actors(self, env):
        actors = []
        for actor_name, actor_id, actor_type  in self.ACTORS:
            if actor_type == ACTOR_TYPE.PERSON:
                actor_data = env.persons[self.env_local[actor_id]]['external_data']
            elif actor_type == ACTOR_TYPE.PLACE:
                actor_data = env.places[self.env_local[actor_id]]['external_data']
            else:
                raise QuestGeneratorException('unknown actor type: %s' % actor_type)
            actors.append((actor_name, actor_type, actor_data))
        return actors


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
