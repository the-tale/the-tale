# coding: utf-8

from django.test import TestCase

from game.quests.quests_generator import commands as cmd
from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.environment import BaseEnvironment
from game.quests.quests_generator.lines import BaseQuestsSource
from game.quests.quests_generator.exceptions import QuestGeneratorException, RollBackException
from game.quests.quests_generator.lines import DeliveryLine
from game.quests.quests_generator.quest_line import Line, Quest
from game.quests.quests_generator.tests.helpers import JustQuest, FakeWriter, FakeQuest

class QuestsSource(BaseQuestsSource):

    quests_list = [DeliveryLine]

    def deserialize_quest(self, data):
        for quest in self.quests_list:
            if data['type'] == quest.type():
                result = quest()
                result.deserialize(data)
                return result
        return None

quests_source = QuestsSource()

class EnvironmentTest(TestCase):

    def setUp(self):
        self.knowlege_base = KnowlegeBase()
        self.knowlege_base.add_place('place_1')
        self.knowlege_base.add_place('place_2')
        self.knowlege_base.add_person('person_1', place='place_1', external_data={})
        self.knowlege_base.add_person('person_2', place='place_2', external_data={})
        self.knowlege_base.initialize()

        self.env = BaseEnvironment(quests_source=quests_source, writers_constructor=FakeWriter, knowlege_base=self.knowlege_base)

    def test_after_constuction(self):
        self.assertEqual(self.env.items_number, 0)
        self.assertEqual(self.env.quests_number, 0)
        self.assertEqual(self.env.lines_number, 0)
        self.assertEqual(self.env.choices_number, 0)

        self.assertEqual(self.env.places, {})
        self.assertEqual(self.env.persons, {})
        self.assertEqual(self.env.items, {})
        self.assertEqual(self.env.quests, {})
        self.assertEqual(self.env.lines, {})
        self.assertEqual(self.env.choices, {})
        self.assertEqual(self.env.persons_power_points, {})

        self.assertEqual(self.env._root_quest, None)

    def test_new_place(self):
        place_uuid = self.env.new_place()
        self.assertTrue(place_uuid in self.knowlege_base.places)
        self.assertTrue(place_uuid in self.env.places)

        place_uuid = self.env.new_place(place_uuid='place_2')
        self.assertTrue(place_uuid in self.knowlege_base.places)
        self.assertTrue(place_uuid in self.env.places)

        place_uuid_copy = self.env.new_place(place_uuid='place_2')
        self.assertEqual(place_uuid, place_uuid_copy)

        self.assertRaises(QuestGeneratorException, self.env.new_place, place_uuid='wrong_place_uuid')

    def test_new_place_limit(self):
        self.assertEqual(set([self.env.new_place(), self.env.new_place()]), set(['place_1', 'place_2']))
        self.assertRaises(RollBackException, self.env.new_place)

    def test_new_person(self):
        self.assertRaises(QuestGeneratorException, self.env.new_person, 'wrong_place_uuid')
        self.assertRaises(QuestGeneratorException, self.env.new_person, 'place_1', person_uuid='wron_person_uuid')

        self.env.new_place(place_uuid='place_1')
        self.env.new_place(place_uuid='place_2')

        person_uuid = self.env.new_person('place_1')
        self.assertTrue(person_uuid in self.knowlege_base.persons)
        self.assertTrue(person_uuid in self.env.persons)

        person_uuid = self.env.new_person('place_2', person_uuid='person_2')
        self.assertTrue(person_uuid in self.knowlege_base.persons)
        self.assertTrue(person_uuid in self.env.persons)

        person_uuid_copy = self.env.new_person('place_2', person_uuid='person_2')
        self.assertEqual(person_uuid, person_uuid_copy)

    def test_new_person_limit(self):
        self.env.new_place(place_uuid='place_1')
        self.env.new_place(place_uuid='place_2')

        self.assertEqual(set([self.env.new_person('place_1'), self.env.new_person('place_2')]), set(['person_1', 'person_2']))
        self.assertRaises(RollBackException, self.env.new_person, 'place_1')
        self.assertRaises(RollBackException, self.env.new_person, 'place_2')

    def test_new_item(self):
        self.assertEqual(self.env.new_item(), 'item_1')
        self.assertEqual(self.env.new_item(), 'item_2')
        self.assertEqual(self.env.new_item(), 'item_3')

    def test_new_choice_point(self):
        self.assertEqual(self.env.new_choice_point(), 'choice_1')
        self.assertEqual(self.env.new_choice_point(), 'choice_2')
        self.assertEqual(self.env.new_choice_point(), 'choice_3')

    def test_new_quest(self):
        self.assertEqual(self.env.new_quest(), 'quest_1')
        self.assertTrue(isinstance(self.env.root_quest, Quest))

    def test_new_quest_with_place(self):
        place_1 = self.env.new_place(place_uuid='place_1')
        self.assertEqual(self.env.new_quest(place_start=place_1), 'quest_1')
        self.assertTrue(isinstance(self.env.root_quest, Quest))

    def test_new_quest_with_person(self):
        place_2 = self.env.new_place(place_uuid='place_2')
        person_2 = self.env.new_person(place_2)
        self.assertRaises(QuestGeneratorException, self.env.new_quest, person_start=person_2)

    def test_new_quest_with_place_and_person(self):
        place_2 = self.env.new_place(place_uuid='place_2')
        person_2 = self.env.new_person(place_2)
        self.assertEqual(self.env.new_quest(place_start=place_2, person_start=person_2), 'quest_1')
        self.assertTrue(isinstance(self.env.root_quest, Quest))

    def test_new_line(self):
        self.assertEqual(self.env.new_line(Line()), 'line_1')
        self.assertEqual(self.env.new_line(Line()), 'line_2')
        self.assertEqual(self.env.new_line(Line()), 'line_3')


    def test_wrappers(self):
        # for tests of methods:
        #
        #     get_start_pointer
        #     increment_pointer
        #     get_quest
        #     get_command
        #     percents
        #
        # see QuestTest class
        pass

    def test_get_writers_text_chain(self):
        quest = JustQuest()
        quest.initialize('quest', self.env)
        quest.create_line(self.env)

        self.env.quests[self.env._root_quest] = quest
        self.env.quests['quest_1'] = FakeQuest(13)

        self.assertEqual(self.env.get_writers_text_chain('hero', [0]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'move',
                           'action_text': 'hero_justquest_event_3_1'}])

        self.assertEqual(self.env.get_writers_text_chain('hero', [1]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'choose',
                           'action_text': 'hero_justquest_event_3_2'}])

        self.assertEqual(self.env.get_writers_text_chain('hero', [1, 'line_1', 7]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'givepower',
                           'action_text': 'hero_justquest_event_1_8'}])

        self.assertRaises(QuestGeneratorException, self.env.get_writers_text_chain, 'hero', [1, 'line_1', 7, 8])
        self.assertRaises(QuestGeneratorException, self.env.get_writers_text_chain, 'hero', [1, 'line_1', 8])

        self.assertEqual(self.env.get_writers_text_chain('hero', [1, 'line_2', 1]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'quest',
                           'action_text': 'hero_justquest_event_2_2'}])

        self.assertEqual(self.env.get_writers_text_chain('hero', [1, 'line_2', 1, 0]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'quest',
                           'action_text': 'hero_justquest_event_2_2'},
                           {'quest_type': 'fakequest',
                           'quest_text': 'hero_fakequest',
                           'action_type': 'fakecmd',
                           'action_text': 'hero_fakequest_fake_event'}])

        self.assertEqual(self.env.get_writers_text_chain('hero', [1, 'line_2', 1, 2]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'quest',
                           'action_text': 'hero_justquest_event_2_2'},
                           {'quest_type': 'fakequest',
                           'quest_text': 'hero_fakequest',
                           'action_type': 'fakecmd',
                           'action_text': 'hero_fakequest_fake_event'}])

        self.assertEqual(self.env.get_writers_text_chain('hero', [1, 'line_2', 2]),
                         [{'quest_type': 'justquest',
                           'quest_text': 'hero_justquest',
                           'action_type': 'getreward',
                           'action_text': 'hero_justquest_event_2_3'}])

        self.assertRaises(QuestGeneratorException, self.env.get_writers_text_chain, 'hero', [1, 'line_2', 3])


    def test_get_nearest_quest_choice(self):
        quest = JustQuest()
        quest.initialize('quest', self.env)
        quest.create_line(self.env)

        self.env.quests[self.env._root_quest] = quest
        self.env.quests['quest_1'] = FakeQuest(13)

        cmd_choose = cmd.Choose(id='choose_1',
                                default='choice_1',
                                choices={'choice_1': 'line_1',
                                         'choice_2': 'line_2' },
                                event='event_3_2',
                                choice='choice_id_1')


        self.assertEqual(self.env.get_nearest_quest_choice([0]), cmd_choose)
        self.assertEqual(self.env.get_nearest_quest_choice([1]), cmd_choose)
        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_1', 0]), None)
        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_1', 7]), None)
        self.assertRaises(QuestGeneratorException, self.env.get_nearest_quest_choice, [1, 'line_1', 7, 8])
        self.assertRaises(QuestGeneratorException, self.env.get_nearest_quest_choice, [1, 'line_1', 8])

        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_2', 0]), None)
        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_2', 1]), None)
        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_2', 1, 0]), None)
        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_2', 1, 2]), None)
        self.assertEqual(self.env.get_nearest_quest_choice([1, 'line_2', 2]), None)
        self.assertRaises(QuestGeneratorException, self.env.get_nearest_quest_choice, [1, 'line_2', 3])

    def test_serialization(self):
        self.env.new_quest()
        self.env.create_lines()

        data = self.env.serialize()

        new_env = BaseEnvironment(quests_source=quests_source, writers_constructor=FakeWriter, knowlege_base=self.knowlege_base)
        new_env.deserialize(data)

        self.assertEqual(self.env, new_env)
