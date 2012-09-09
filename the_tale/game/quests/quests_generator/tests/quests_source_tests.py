# coding: utf-8

from django.test import TestCase

from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.environment import BaseEnvironment
from game.quests.quests_generator.quests_source import BaseQuestsSource
from game.quests.quests_generator.tests.helpers import JustQuest, FakeWriter, FakeQuest, QuestNoChoice

class QuestsSource(BaseQuestsSource):

    quests_list = [JustQuest, QuestNoChoice, FakeQuest]


class QuestsSourceTest(TestCase):

    def setUp(self):
        self.knowlege_base = KnowlegeBase()
        self.knowlege_base.add_place('place_1')
        self.knowlege_base.add_place('place_2')
        self.knowlege_base.add_person('person_1', place='place_1', external_data={})
        self.knowlege_base.add_person('person_2', place='place_2', external_data={})
        self.knowlege_base.initialize()

        self.quests_source = QuestsSource()

        self.env = BaseEnvironment(quests_source=self.quests_source, writers_constructor=FakeWriter, knowlege_base=self.knowlege_base)


    def test_filter_all(self):
        self.assertEqual(self.quests_source.filter(self.env),
                         [JustQuest, QuestNoChoice, FakeQuest])

    def test_filter_exclude(self):
        self.assertEqual(self.quests_source.filter(self.env, excluded_list=['justquest', 'fakequest']),
                         [QuestNoChoice])

    def test_filter_from_list(self):
        self.assertEqual(self.quests_source.filter(self.env, from_list=['justquest', 'fakequest']),
                         [JustQuest, FakeQuest])

    def test_filter_from_list_and_exclude(self):
        self.assertEqual(self.quests_source.filter(self.env, from_list=['justquest', 'fakequest'], excluded_list=['fakequest']),
                         [JustQuest])
