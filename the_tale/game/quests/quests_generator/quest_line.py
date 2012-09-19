# coding: utf-8
import copy
import random

from game.quests.quests_generator.exceptions import QuestGeneratorException
from game.quests.quests_generator.environment import LocalEnvironment
from game.quests.quests_generator.commands import deserialize_command

class ACTOR_TYPE:
    PERSON = 0
    PLACE = 1


class DEFAULT_RESULTS:
    POSITIVE = 'positive'
    NEGATIVE = 'negative'


class Line(object):

    def __init__(self, sequence=[]):
        self.sequence = [element for element in sequence if element is not None]
        self.available = None

        # temporary storage for real power changes (such changes, that necessary be at that line)
        self._power_changes = {}

    def get_start_pointer(self):
        return [0]

    def calculate_changes(self, env, powers):
        '''
        This method calculated power changes ended on tree node, witch is processed now (NOT DEEPER)
        On basis of this check, self.calculate_availablity(...) take desision about line availablilty
        On this level we are not intrested in deeper nodes, information from them will be processed in self.calculate_availablity(...)
        '''
        powers = copy.copy(powers) + [cmd for cmd in reversed(self.sequence) if cmd.is_givepower]

        for cmd in self.sequence:
            if cmd.is_quest:
                env.quests[cmd.quest].calculate_changes(env, powers)
            elif cmd.is_choice:
                for line in cmd.choices.values():
                    env.lines[line].calculate_changes(env, powers)
            elif cmd.is_switch:
                for condition, line in cmd.choices:
                    env.lines[line].calculate_changes(env, powers)

        for cmd in reversed(powers):
            self._power_changes[cmd.person] = self._power_changes.get(cmd.person,0) + cmd.power

    def reset_availability(self, env):
        '''
        reset availability from True to None
        '''
        self.available = None

        for cmd in self.sequence:
            if cmd.is_quest:
                env.quests[cmd.quest].reset_availability(env)
            elif cmd.is_choice:
                for line_id in cmd.choices.values():
                    env.lines[line_id].reset_availability(env)
            elif cmd.is_switch:
                for condition, line_id in cmd.choices:
                    env.lines[line_id].reset_availability(env)



    def calculate_availability(self, env, current_quest_id, blocked_quests_results, current_quest_results, direct_quests_results):
        '''
        direct_quests_results are empty dict on quest main line (see Quest.calculate_availability(...))
        blocked_quests_results - dict of sets with all blocked quests results
        current_quest_results - available results of current quest
        direct_quests_results - result of direct child of current quest, that ended before current line
        we can use only direct child quest in switch checks

        we do multi-pass check (implemented in Quest.calculate_availability(...)),
        if line already unavailable, we skip check, else do full check
        '''

        if self.available is not None and not self.available:
            # print current_quest_id,  'False: 1'
            return False

        # check friend restrictions
        friend_data = env.knowlege_base.get_special('hero_pref_friend')
        friend_uuid = friend_data['uuid'] if friend_data else None

        if friend_uuid and self._power_changes.get(friend_uuid, 0) < 0:
            self.available = False
            # print current_quest_id, 'False: 2'
            return False

        # check enemy restrictions
        enemy_data = env.knowlege_base.get_special('hero_pref_enemy')
        enemy_uuid = enemy_data['uuid'] if enemy_data else None

        if enemy_uuid and self._power_changes.get(enemy_uuid, 0) > 0:
            self.available = False
            # print current_quest_id,  'False: 3'
            return False

        local_current_quest_results = copy.deepcopy(current_quest_results)
        local_direct_quests_results = copy.deepcopy(direct_quests_results)

        for cmd in self.sequence:
            if cmd.is_quest:
                quests_results = set()
                if not env.quests[cmd.quest].calculate_availability(env, blocked_quests_results, quests_results):
                    self.available = False
                    # print current_quest_id,  'False: 4'
                    return False

                if cmd.quest not in local_direct_quests_results:
                    local_direct_quests_results[cmd.quest] = set()

                local_direct_quests_results[cmd.quest] |= quests_results

            elif cmd.is_choice:
                for line_id in cmd.choices.values():
                    line = env.lines[line_id]
                    line.calculate_availability(env, current_quest_id, blocked_quests_results, local_current_quest_results, local_direct_quests_results)

                if not any(env.lines[line].available for line in cmd.choices.values()):
                    self.available = False
                    # print current_quest_id,  'False: 5'
                    return False

            elif cmd.is_switch:
                for condition, line_id in cmd.choices:
                    line = env.lines[line_id]

                    quest_id, quest_result = condition
                    if quest_id not in local_direct_quests_results or quest_result not in local_direct_quests_results[quest_id]:
                        # print current_quest_id,  'False: 7 (without return)'
                        line.available = False
                    else:
                        line.calculate_availability(env, current_quest_id, blocked_quests_results, local_current_quest_results, local_direct_quests_results)

                    # print condition, line.available

                    if not line.available:
                        if quest_id not in blocked_quests_results:
                            blocked_quests_results[quest_id] = set()
                        blocked_quests_results[quest_id].add(quest_result)

                if not any(env.lines[line_id].available for condition, line_id in cmd.choices):
                    self.available = False
                    return False


            elif cmd.is_quest_result:
                local_current_quest_results.add(cmd.result)

                # print 'blocked', current_quest_id, blocked_quests_results

                # check availability
                if current_quest_id not in blocked_quests_results:
                    continue
                if cmd.result in blocked_quests_results[current_quest_id]:
                    self.available = False
                    # print current_quest_id,  'False: 6 (result: %s)'% cmd.result
                    return False

        current_quest_results.update(local_current_quest_results)
        direct_quests_results.update(local_direct_quests_results)

        # print current_quest_id, 'True'
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
            elif cmd.is_switch:
                number += max(env.lines[line].get_commands_number(env) for condition, line in cmd.choices)

        if pointer and len(pointer) > 1:
            cmd = self.sequence[cmd_number]
            if cmd.is_quest:
                number += 1 + env.quests[cmd.quest].get_commands_number(env, pointer[1:])
            elif cmd.is_choice or cmd.is_switch:
                number += 1 + env.lines[pointer[1]].get_commands_number(env, pointer[2:])
            else:
                raise QuestGeneratorException('command has no attribute "quest" or "choices", cmd is: %r' % cmd.serialize())

        return number

    def increment_pointer(self, env, pointer, choices):
        '''
        pointer: [x, p1, ..., pn]

        interetation:

        [x is quest, p[1..n] pointer in child quest line]
        [x is choice, p1 - line id, p[2..n] pointer in child line]
        [x is choice, p1 - switch number id, p[2..n] pointer in child line]

        alternative explanation:

        [x - cmd number]
        [x - line id, p1 - cmd number in line]
        '''

        if pointer[0] >= len(self.sequence):
            raise QuestGeneratorException('increment pointer: wrong pointer value (%r) for this line' % pointer)

        cmd = self.sequence[pointer[0]]

        if len(pointer) == 1:

            if cmd.is_quest:
                return [pointer[0]] + self.get_start_pointer()

            if cmd.is_choice:
                default_choices = [ choice
                                    for choice, line_id in cmd.choices.items()
                                    if env.lines[line_id].available ]
                if not default_choices:
                    raise QuestGeneratorException('no available lines in choices - quest must be rolled back on generation step')

                player_choice = choices.get(cmd.id)
                if player_choice is not None and player_choice not in default_choices:
                    raise QuestGeneratorException('player chosen not available line')

                choice = player_choice if player_choice is not None else random.choice(default_choices)

                choosed_line = cmd.choices[choice]
                return [pointer[0], choosed_line] + env.lines[choosed_line].get_start_pointer()

            if cmd.is_switch:

                switch_number = None
                switch_line_id = None

                for index, (condition, line_id) in enumerate(cmd.choices):
                    quest_id, result = condition

                    if quest_id not in env.quests_results:
                        continue

                    if result in env.quests_results[quest_id]:
                        switch_number = index
                        switch_line_id = line_id
                        break

                if switch_number is None:
                    raise QuestGeneratorException('can not find suitable switch')

                return [pointer[0], switch_line_id] + env.lines[switch_line_id].get_start_pointer()

            if len(self.sequence) > pointer[0]+1:
                return [pointer[0]+1]

            return None

        if cmd.is_quest:
            prev_subpointer = pointer[0:1]
            next_subpointer = env.quests[self.sequence[pointer[0]].quest].increment_pointer(env, pointer[1:], choices)

        if cmd.is_choice or cmd.is_switch:
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

        if not cmd.is_choice and not cmd.is_switch:
            return cmd, choices, pointer[1:]

        if len(pointer) == 1:
            return cmd, choices, []

        if cmd.is_choice:
            if pointer[1] not in cmd.choices.values():
                raise QuestGeneratorException(u'choose cmd: wrong pointer "%r" - line "%s" not in choice "%s"' % (pointer, pointer[1], cmd.get_description(env)))

            choices.append((cmd.choice, cmd.get_choice_by_line(pointer[1])))
            return env.lines[pointer[1]].get_quest_command(env, pointer[2:], choices=choices)

        if cmd.is_switch:
            if pointer[1] not in [line_id for condition, line_id in cmd.choices]:
                raise QuestGeneratorException(u'switch cmd: wrong pointer "%r" - line "%s" not in choice "%s"' % (pointer, pointer[1], cmd.get_description(env)))

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

    def calculate_changes(self, env, powers):
        return env.lines[self.line].calculate_changes(env, powers)

    def reset_availability(self, env):
        env.lines[self.line].reset_availability(env)
        self.available = None


    def calculate_availability(self, env, blocked_quests_results, current_quest_results):
        old_blocked_results_number = sum([len(results) for results in blocked_quests_results.values()])

        while True:
            # print '-', self.id, '--------------'

            self.available = env.lines[self.line].calculate_availability(env,
                                                                         self.id,
                                                                         blocked_quests_results=blocked_quests_results,
                                                                         current_quest_results=current_quest_results,
                                                                         direct_quests_results={})

            blocked_resultes_number = sum([len(results) for results in blocked_quests_results.values()])

            if blocked_resultes_number == old_blocked_results_number:
                return self.available

            old_blocked_results_number = blocked_resultes_number

            self.reset_availability(env)

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
