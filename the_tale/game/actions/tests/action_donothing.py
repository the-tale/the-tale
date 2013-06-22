# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.logic_storage import LogicStorage
from game.actions.prototypes import ActionDoNothingPrototype
from game.prototypes import TimePrototype


class DoNothingActionTest(testcase.TestCase):

    @mock.patch('game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(DoNothingActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.action_donothing = ActionDoNothingPrototype.create(hero=self.hero, duration=7, messages_prefix='abrakadabra', messages_probability=0.3)


    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_donothing.leader, True)
        self.assertEqual(self.action_donothing.textgen_id, 'abrakadabra')
        self.assertEqual(self.action_donothing.percents_barier, 7)
        self.assertEqual(self.action_donothing.extra_probability, 0.3)
        self.assertEqual(self.action_donothing.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_donothing)
        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(7):
            self.assertEqual(len(self.hero.actions.actions_list), 2)
            self.assertTrue(self.action_donothing.leader)
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()
