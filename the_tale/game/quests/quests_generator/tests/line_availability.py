# coding: utf-8

from django.test import TestCase

from game.quests.quests_generator.quest_line import Line, Quest
from game.quests.quests_generator import commands as cmd
from game.quests.quests_generator.environment import BaseEnvironment
from game.quests.quests_generator.quests_source import BaseQuestsSource
from game.quests.quests_generator.knowlege_base import KnowlegeBase

def get_quests_source(person_1_power, person_2_power, person_3_power):

    class SimplePowerQuest(Quest):

        def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
            super(SimplePowerQuest, self).initialize(identifier, env)

            self.env_local.register('place_start', place_start or env.new_place())
            self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
            self.env_local.register('place_end', place_end or env.new_place())
            self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        def create_line(self, env):
            main_line = Line(sequence=[cmd.GivePower(event='event_', person=self.env_local.person_end, power=person_3_power)])
            self.line = env.new_line(main_line)


    class PowerQuest(Quest):

        def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
            super(PowerQuest, self).initialize(identifier, env)

            self.env_local.register('place_start', place_start or env.new_place())
            self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
            self.env_local.register('place_end', place_end or env.new_place())
            self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

            self.env_local.register('power_quest', env.new_quest(from_list=['simplepowerquest'],
                                                                 place_start=self.env_local.place_start,
                                                                 place_end=self.env_local.place_end,
                                                                 person_start=self.env_local.person_start,
                                                                 person_end=env.new_person(from_place=self.env_local.place_end)))


        def create_line(self, env):
            linear_line = Line(sequence=[cmd.GivePower(event='event_', person=self.env_local.person_start, power=person_1_power) ])
            linear_line_2 = Line(sequence=[cmd.GivePower(event='event_', person=self.env_local.person_start, power=person_1_power) ])

            main_line = Line(sequence=[cmd.Quest(event='event_', quest=self.env_local.power_quest),
                                       cmd.Choose(id='choose_1',
                                                  default='choice_1',
                                                  choices={'choice_1': env.new_line(linear_line),
                                                           'choice_2': env.new_line(linear_line_2) },
                                                  event='event_',
                                                  choice='choice_id_1'),
                                        cmd.GivePower(event='event_', person=self.env_local.person_end, power=person_2_power)])
            self.line = env.new_line(main_line)
            env.quests[self.env_local.power_quest].create_line(env)


    class QuestsSource(BaseQuestsSource):

        quests_list = [PowerQuest, SimplePowerQuest]

        def deserialize_quest(self, data):
            for quest in self.quests_list:
                if data['type'] == quest.type():
                    result = quest()
                    result.deserialize(data)
                    return result
            return None

    return QuestsSource()

writers_constructor = lambda hero, quest_type, env, quest_env_local: 0


class LineAvailabilityTest(TestCase):

    def setUp(self):
        pass

    def create_quest(self, person_1_power, person_2_power, person_3_power, friend=None):
        self.knowlege_base = KnowlegeBase()

        self.knowlege_base.add_place('place_1')
        self.knowlege_base.add_person('person_1', place='place_1')
        self.knowlege_base.add_person('person_2', place='place_1')
        self.knowlege_base.add_person('person_3', place='place_1')

        if friend:
            self.knowlege_base.add_special('hero_pref_friend', {'uuid': friend})

        self.knowlege_base.initialize()

        self.env = BaseEnvironment(quests_source=get_quests_source(person_1_power=person_1_power, person_2_power=person_2_power, person_3_power=person_3_power),
                                   writers_constructor=writers_constructor,
                                   knowlege_base=self.knowlege_base)
        place_id = self.env.new_place()
        self.env.new_quest(from_list=['powerquest'],
                           place_start=place_id,
                           person_start=self.env.new_person(from_place=place_id, person_uuid='person_1'),
                           place_end=place_id,
                           person_end=self.env.new_person(from_place=place_id, person_uuid='person_2') )

        self.env.create_lines()

    def check_quest(self, quests=[], lines=[]):
        self.assertEqual(self.env.root_quest.available, quests[0])
        self.assertEqual(self.env.quests['quest_2'].available, quests[1])

        self.assertEqual(self.env.lines['line_1'].available, lines[0]) # first choice line
        self.assertEqual(self.env.lines['line_2'].available, lines[1]) # second choice line
        self.assertEqual(self.env.lines['line_3'].available, lines[2]) # main line
        self.assertEqual(self.env.lines['line_4'].available, lines[3]) # quest line


    def test_availability(self):
        self.create_quest(1, 1, 1)
        self.check_quest([True, True],
                         [True, True, True, True])

    def test_simple_power_quest_not_availability(self):
        self.create_quest(1, 1, -1, friend='person_3')
        self.check_quest([False, False],
                         [None, None, False, False])

    def test_choices_not_availability(self):
        self.create_quest(-1, 1, 1, friend='person_1')
        self.check_quest([False, True],
                         [False, False, False, True])


    def test_main_line_not_availability(self):
        self.create_quest(1, -1, 1, friend='person_2')
        self.check_quest([False, None],
                         [None, None, False, None])
