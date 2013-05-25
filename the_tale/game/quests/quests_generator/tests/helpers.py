# coding: utf-8

import mock

from game.quests.quests_generator.quests_source import BaseQuestsSource
from game.quests.quests_generator.quest_line import Quest, Line
from game.quests.quests_generator import commands as cmd

class FakeWriter(object):

    def __init__(self, hero, quest_type, env, env_local):
        self.hero = hero
        self.quest_type = quest_type
        self.env = env
        self.env_local = env_local

    def get_description_msg(self):
        return '%s_%s' % (str(self.hero), self.quest_type)

    def get_action_msg(self, event):
        return '%s_%s_%s' % (str(self.hero), self.quest_type, event)

    def get_choice_result_msg(self, choice, answer):
        return '%s_%s_%s_%s' % (str(self.hero), self.quest_type, choice, answer)


class FakeCmd(cmd.Command): pass


class FakeLine(Line):

    def get_quest_command(self, env, pointer):
        return FakeCmd('fake_event'), [], []

class FakeQuest(Quest):

    def __init__(self, commands_number=13):
        super(FakeQuest, self).__init__()
        self.commands_number = commands_number

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(FakeQuest, self).initialize(identifier, env)

    def create_line(self, env):
        self.line = env.new_line(FakeLine())

    def get_commands_number(self, env, pointer=None):
        if pointer:
            return pointer[0]
        return self.commands_number

    def increment_pointer(self, env, pointer, choices):
        next_poiner = list(pointer)
        if pointer[-1] < self.commands_number - 1:
            next_poiner[-1] += 1
            return next_poiner

        return None


class JustQuest(Quest):

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(JustQuest, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('quest_1', env.new_quest(from_list=['fakequest'],
                                                         place_start=self.env_local.place_start,
                                                         place_end=self.env_local.place_end,
                                                         person_start=self.env_local.person_start,
                                                         person_end=self.env_local.person_end))


    def create_line(self, env):
        linear_line = Line(sequence=[cmd.Move(event='event_1_1', place='place_1'),
                                     cmd.MoveNear(event='event_1_2', place='place_1', back=False),
                                     cmd.MoveNear(event='event_1_3', place='place_1', back=True),
                                     cmd.GetItem(event='event_1_4', item='item_1'),
                                     cmd.GiveItem(event='event_1_5', item='item_1'),
                                     cmd.Battle(event='event_1_6', number=13),
                                     cmd.GetReward(event='event_1_7', person='person_1'),
                                     cmd.GivePower(event='event_1_8', person='person_1', power=2) ])

        quest_line = Line(sequence=[cmd.Move(event='event_2_1', place='place_2'),
                                    cmd.Quest(event='event_2_2', quest=self.env_local.quest_1),
                                    cmd.GetReward(event='event_2_3', person='person_2')  ])

        main_line = Line(sequence=[cmd.Move(event='event_3_1', place='place_3'),
                                   cmd.Choose(id='choose_1',
                                              default='choice_1',
                                              choices={'choice_1': env.new_line(linear_line),
                                                       'choice_2': env.new_line(quest_line) },
                                              event='event_3_2',
                                              choice='choice_id_1'),
                                   cmd.Battle(event='event_3_3', number=13) ])
        self.line = env.new_line(main_line)
        env.quests[self.env_local.quest_1].create_line(env)


class QuestWith2ChoicePoints(Quest):

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(QuestWith2ChoicePoints, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('quest_1', 'quest_1')

    def create_line(self, env):
        line_1 = Line(sequence=[cmd.Battle(event='event_1_1', number=1),
                                cmd.GetReward(event='event_1_2', person='person_1'),
                                cmd.GivePower(event='event_1_3', person='person_1', power=2)  ])

        line_3 = Line(sequence=[cmd.Battle(event='event_3_1', number=1),
                                cmd.GetReward(event='event_3_2', person='person_1'),
                                cmd.GivePower(event='event_3_3', person='person_1', power=2)  ])

        line_4 = Line(sequence=[cmd.Battle(event='event_4_1', number=1),
                                cmd.GetReward(event='event_4_2', person='person_1'),
                                cmd.GivePower(event='event_4_3', person='person_1', power=2)  ])

        line_2 = Line(sequence=[cmd.Battle(event='event_2_1', number=1),
                                cmd.Choose(id='choose_2',
                                           default='choice_2_1',
                                           choices={'choice_2_1': env.new_line(line_3),
                                                    'choice_2_2': env.new_line(line_4) },
                                            event='event_2_2',
                                            choice='choice_id_2') ])

        main_line = Line(sequence=[cmd.Battle(event='event_0_1', number=1),
                                   cmd.Choose(id='choose_1',
                                              default='choice_1_1',
                                              choices={'choice_1_1': env.new_line(line_1),
                                                       'choice_1_2': env.new_line(line_2) },
                                              event='event_0_2',
                                              choice='choice_id_1')  ])
        self.line = env.new_line(main_line)


class QuestNoChoice(Quest):

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(QuestNoChoice, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

    def create_line(self, env):

        main_line = Line(sequence=[cmd.Battle(event='event_0_1', number=1) ])
        self.line = env.new_line(main_line)


def patch_quests_list(prefix, quests_list):

    def decorator(func):
        # func = mock.patch('game.quests.quests_generator.lines.QUESTS', quests_list)(func)
        # func = mock.patch('game.quests.quests_generator.lines.QUESTS_TYPES', [q.type() for q in quests_list])(func)
        func = mock.patch('%s.quests_list' % prefix, quests_list)(func)
        return func

    return decorator


class QuestsSource(BaseQuestsSource):

    quests_list = [JustQuest, QuestNoChoice, FakeQuest]

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None
