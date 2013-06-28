# coding: utf-8
import mock
import datetime

from common.utils import testcase

from common.utils.fake import FakeWorkerCommand

from accounts.logic import register_user

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.prototypes import TimePrototype

from game.actions.prototypes import ActionQuestPrototype

from game.heroes.prototypes import HeroPrototype

from game.quests.logic import create_random_quest_for_hero
from game.quests.prototypes import QuestPrototype


class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.quest = create_random_quest_for_hero(self.hero)
        self.action_quest = ActionQuestPrototype.create(hero=self.hero, quest=self.quest)

    def tearDown(self):
        pass

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

    def test_initialization(self):
        self.assertEqual(TimePrototype.get_current_turn_number(), self.hero.quests_history[self.quest.env.root_quest.type()])


    @mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', lambda *args, **kwargs: 1)
    def test_power_on_end_quest_for_fast_account_hero(self):
        fake_cmd = FakeWorkerCommand()

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 1)

        self.assertFalse(fake_cmd.commands)

    @mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', lambda *args, **kwargs: 1)
    def test_power_on_end_quest_for_premium_account_hero(self):

        self.hero.is_fast = False
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 1)

        self.assertTrue(fake_cmd.call_count > 0)

    @mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', lambda *args, **kwargs: 1)
    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 1)

        self.assertEqual(fake_cmd.call_count, 0)

    def test_power_on_end_quest__modify_person_power_called(self):

        modify_person_power = mock.Mock(return_value=1)
        with mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', modify_person_power):
            self.hero.is_fast = False
            self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

            self.assertEqual(self.hero.places_history.history, [])

            with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power') as fake_cmd:
                self.complete_quest()

            self.assertTrue(fake_cmd.call_count > 0)
            self.assertTrue(modify_person_power.call_count > 0)

    def test_modify_person_power(self):
        person = self.place_1.persons[0]

        with mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 0.0):
            self.assertEqual(QuestPrototype.modify_person_power(person, 2, 3, 5), 0)

        with mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 7):
            self.assertEqual(QuestPrototype.modify_person_power(person, 2, 3, 5), 2*3*5*7)


    def test_get_minimum_created_time_of_active_quests(self):
        self.assertEqual(self.quest._model.created_at, QuestPrototype.get_minimum_created_time_of_active_quests())

        self.quest.remove()

        # not there are no another quests an get_minimum_created_time_of_active_quests return now()
        self.assertTrue(self.quest._model.created_at < QuestPrototype.get_minimum_created_time_of_active_quests())

    def test_get_experience_for_quest(self):
        self.assertEqual(self.hero.experience, 0)
        self.complete_quest()
        self.assertTrue(self.hero.experience > 0)

    def test_modify_experience(self):
        self.assertEqual(self.quest.modify_experience(100), 100)

        with mock.patch('game.map.places.prototypes.PlacePrototype.get_experience_modifier',
                        mock.Mock(return_value=0.1)) as get_experience_modifier:
            self.assertTrue(self.quest.modify_experience(100) > 100)

        self.assertTrue(get_experience_modifier.call_count > 0)
