# coding: utf-8
import time

from common.utils import testcase

from game.quests.container import QuestsContainer
from game.quests.conf import quests_settings


class ContainerTests(testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()
        self.container = QuestsContainer()


    def test_add_interfered_person(self):
        self.assertFalse(self.container.is_interfered(1))
        self.container.add_interfered_person(1)
        self.assertTrue(self.container.is_interfered(1))

    def test_sync_interfered_person(self):
        self.container.interfered_persons[1] = time.time() - quests_settings.INTERFERED_PERSONS_LIVE_TIME
        self.container.interfered_persons[2] = time.time()

        self.assertTrue(self.container.is_interfered(1))
        self.assertTrue(self.container.is_interfered(2))

        self.container.sync_interfered_person()

        self.assertFalse(self.container.is_interfered(1))
        self.assertTrue(self.container.is_interfered(2))
