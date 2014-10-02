# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.actions.prototypes import ActionDoNothingPrototype
from the_tale.game.prototypes import TimePrototype


class DoNothingActionTest(testcase.TestCase):

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(DoNothingActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.action_donothing = ActionDoNothingPrototype.create(hero=self.hero, duration=7, messages_prefix='QUEST_HOMETOWN_JOURNAL_CHATTING', messages_probability=0.3)


    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_donothing.leader, True)
        self.assertEqual(self.action_donothing.textgen_id, 'QUEST_HOMETOWN_JOURNAL_CHATTING')
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
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()
