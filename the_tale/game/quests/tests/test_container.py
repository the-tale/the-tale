# coding: utf-8
import time

from the_tale.common.utils import testcase

from the_tale.game.quests.container import QuestsContainer
from the_tale.game.quests.conf import quests_settings


class ContainerTests(testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()
        self.container = QuestsContainer()


    def test_add_interfered_person(self):
        self.assertFalse(self.container.is_person_interfered(1))
        self.container.add_interfered_person(1)
        self.assertTrue(self.container.is_person_interfered(1))

    def test_sync_interfered_persons(self):
        self.container.interfered_persons[1] = time.time() - quests_settings.INTERFERED_PERSONS_LIVE_TIME
        self.container.interfered_persons[2] = time.time()
        self.container.interfered_persons[3] = time.time() - quests_settings.INTERFERED_PERSONS_LIVE_TIME + 1

        self.assertFalse(self.container.is_person_interfered(1))
        self.assertTrue(self.container.is_person_interfered(2))
        self.assertTrue(self.container.is_person_interfered(3))

        self.container.sync_interfered_persons()

        self.assertFalse(self.container.is_person_interfered(1))
        self.assertTrue(self.container.is_person_interfered(2))
        self.assertTrue(self.container.is_person_interfered(3))

    def test_excluded_quests__no_history(self):
        self.assertEqual(self.container.history, {})
        self.assertEqual(self.container.excluded_quests(), [])

    def test_excluded_quests__one_history(self):
        self.assertEqual(self.container.history, {})
        self.container.update_history('q_1', 1)
        self.assertEqual(self.container.excluded_quests(), [])

    def test_excluded_quests__big_history__odd(self):
        self.assertEqual(self.container.history, {})

        self.container.update_history('q_1', 5)
        self.container.update_history('q_2', 4)
        self.container.update_history('q_3', 3)
        self.container.update_history('q_4', 2)
        self.container.update_history('q_5', 1)

        self.assertEqual(set(self.container.excluded_quests()), set(['q_1', 'q_2']))

    def test_excluded_quests__big_history__even(self):
        self.assertEqual(self.container.history, {})

        self.container.update_history('q_1', 5)
        self.container.update_history('q_2', 4)
        self.container.update_history('q_3', 3)
        self.container.update_history('q_4', 2)
        self.container.update_history('q_5', 1)
        self.container.update_history('q_6', 0)

        self.assertEqual(set(self.container.excluded_quests()), set(['q_1', 'q_2', 'q_3']))
