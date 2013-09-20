# coding: utf-8
import mock
import datetime

from questgen import facts

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
from game.quests import uids


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

    def get_hero_position_id(self, quest):
        kb = quest.knowledge_base

        hero_position_uid = list(location.place
                                 for location in kb.filter(facts.LocatedIn)
                                 if location.object == uids.hero(self.hero))[0]
        return kb[hero_position_uid].externals['id']

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        # save link to quest, since it will be removed from hero when quest finished
        quest = self.hero.quests.current_quest

        self.assertEqual(self.hero.position.place.id, self.get_hero_position_id(quest))

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.hero.position.place.id, self.get_hero_position_id(quest))
        self.assertTrue(isinstance(quest.knowledge_base[quest.machine.pointer.state], facts.Finish))
        self.assertTrue(all(requirement.check(quest.knowledge_base) for requirement in quest.knowledge_base[quest.machine.pointer.state].require))

        self.assertTrue(self.hero.quests_history[quest.knowledge_base.filter(facts.Start).next().quest_uid] > 0)

    @mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', lambda *args, **kwargs: 1)
    def test_power_on_end_quest_for_fast_account_hero(self):
        fake_cmd = FakeWorkerCommand()

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.highlevel.Worker.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 1)

        self.assertFalse(fake_cmd.commands)

    @mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', lambda *args, **kwargs: 1)
    def test_power_on_end_quest_for_premium_account_hero(self):

        self.hero.is_fast = False
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.highlevel.Worker.cmd_change_person_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 1)

        self.assertTrue(fake_cmd.call_count > 0)

    @mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', lambda *args, **kwargs: 1)
    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.highlevel.Worker.cmd_change_person_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 1)

        self.assertEqual(fake_cmd.call_count, 0)

    def test_power_on_end_quest__modify_person_power_called(self):

        modify_person_power = mock.Mock(return_value=1)
        with mock.patch('game.quests.prototypes.QuestPrototype.modify_person_power', modify_person_power):
            self.hero.is_fast = False
            self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

            self.assertEqual(self.hero.places_history.history, [])

            with mock.patch('game.workers.highlevel.Worker.cmd_change_person_power') as fake_cmd:
                self.complete_quest()

            self.assertTrue(fake_cmd.call_count > 0)
            self.assertTrue(modify_person_power.call_count > 0)

    def test_modify_person_power(self):
        person = self.place_1.persons[0]

        with mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 0.0):
            self.assertEqual(QuestPrototype.modify_person_power(person, 2, 3, 5), 0)

        with mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 7):
            self.assertEqual(QuestPrototype.modify_person_power(person, 2, 3, 5), 2*3*5*7)


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

    @mock.patch('game.balance.formulas.artifacts_per_battle', lambda *argv: 0)
    @mock.patch('game.heroes.prototypes.HeroPrototype.can_get_artifact_for_quest', lambda *argv: False)
    def test_get_money_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertTrue(self.hero.statistics.money_earned_from_quests > 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

    @mock.patch('game.balance.formulas.artifacts_per_battle', lambda *argv: 0)
    @mock.patch('game.heroes.prototypes.HeroPrototype.can_get_artifact_for_quest', lambda *argv: True)
    def test_get_artifacts_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
