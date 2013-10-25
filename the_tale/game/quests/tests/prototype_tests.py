# coding: utf-8
import mock
import datetime

from questgen import facts

from dext.utils import s11n

from common.utils import testcase

from common.utils.fake import FakeWorkerCommand

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.prototypes import TimePrototype

from game.actions.prototypes import ActionQuestPrototype

from game.quests.logic import create_random_quest_for_hero
from game.quests.prototypes import QuestPrototype
from game.quests import uids
from game.quests import exceptions


class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.action_idl.state = self.action_idl.STATE.QUEST

        self.quest = create_random_quest_for_hero(self.hero)
        self.action_quest = ActionQuestPrototype.create(hero=self.hero, quest=self.quest)


    def test_serialization(self):
        self.assertEqual(self.quest.serialize(), QuestPrototype.deserialize(self.hero, self.quest.serialize()).serialize())

    def get_hero_position_id(self, quest):
        kb = quest.knowledge_base

        hero_position_uid = (location.place
                             for location in kb.filter(facts.LocatedIn)
                             if location.object == uids.hero(self.hero)).next()
        return kb[hero_position_uid].externals['id']

    def test_replane_required__reset_on_do_step(self):
        self.quest.replane_required = True
        self.quest.do_step()
        self.assertFalse(self.quest.replane_required)

    def test_do_step(self):
        self.hero.quests.updated = False
        self.quest.process()
        self.assertTrue(self.hero.quests.updated)

    def complete_quest(self, callback=lambda : None):
        current_time = TimePrototype.get_current_time()

        # save link to quest, since it will be removed from hero when quest finished
        quest = self.hero.quests.current_quest

        self.assertEqual(self.hero.position.place.id, self.get_hero_position_id(quest))

        old_quests_done = self.hero.statistics.quests_done

        while not self.action_idl.leader:
            self.storage.process_turn()
            callback()
            current_time.increment_turn()

        self.assertEqual(self.hero.position.place.id, self.get_hero_position_id(quest))
        self.assertTrue(isinstance(quest.knowledge_base[quest.machine.pointer.state], facts.Finish))
        self.assertTrue(all(requirement.check(quest.knowledge_base) for requirement in quest.knowledge_base[quest.machine.pointer.state].require))

        self.assertTrue(self.hero.quests.history[quest.knowledge_base.filter(facts.Start).next().type] > 0)

        self.assertTrue(old_quests_done < self.hero.statistics.quests_done)

    def check_ui_info(self):
        s11n.to_json(self.hero.ui_info())

    def test_complete_quest(self):
        self.assertEqual(self.hero.quests.interfered_persons, {})
        self.complete_quest(self.check_ui_info)
        self.assertNotEqual(self.hero.quests.interfered_persons, {})

    @mock.patch('game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_fast_account_hero(self):
        fake_cmd = FakeWorkerCommand()

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.highlevel.Worker.cmd_change_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertFalse(fake_cmd.commands)

    @mock.patch('game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_premium_account_hero(self):

        self.hero.is_fast = False
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertTrue(fake_cmd.call_count > 0)

    @mock.patch('game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertEqual(fake_cmd.call_count, 0)

    def test_power_on_end_quest__give_power_called(self):

        with mock.patch('game.quests.prototypes.QuestPrototype._give_power') as give_power:
            self.hero.is_fast = False
            self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

            self.assertEqual(self.hero.places_history.history, [])

            with mock.patch('game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
                self.complete_quest()

            self.assertTrue(fake_cmd.call_count > 0)

        self.assertTrue(give_power.call_count > 0)

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

    def test_satisfy_requirement__unknown(self):
        self.assertRaises(exceptions.UnknownRequirement, self.quest.satisfy_requirement, facts.Start(uid='start', type='test', nesting=0))

    def test_do_actions__unknown(self):
        self.assertRaises(exceptions.UnknownAction, self.quest._do_actions, [facts.Start(uid='start', type='test', nesting=0)])

    def test_get_upgrdade_choice__no_preference(self):
        for i in xrange(100):
            self.assertEqual(self.quest._get_upgrdade_choice(self.hero), 'buy')

    def test_get_upgrdade_choice(self):
        from game.heroes.relations import EQUIPMENT_SLOT

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)

        choices = set()

        for i in xrange(100):
            choices.add(self.quest._get_upgrdade_choice(self.hero))

        self.assertEqual(choices, set(('buy', 'sharp')))


    def test_get_upgrdade_choice__no_item_equipped(self):
        from game.heroes.relations import EQUIPMENT_SLOT

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.RING)

        for i in xrange(100):
            self.assertEqual(self.quest._get_upgrdade_choice(self.hero), 'buy')


    @mock.patch('game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: 'buy'))
    def test_upgrade_equipment__buy(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.quest._upgrade_equipment(process_message=self.quest.quests_stack[-1].process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    @mock.patch('game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: 'sharp'))
    def test_upgrade_equipment__sharp(self):
        old_power = self.hero.power
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

        self.quest._upgrade_equipment(process_message=self.quest.quests_stack[-1].process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(old_power + 1, self.hero.power)

    def test_upgrade_equipment__money_limit(self):
        self.hero._model.money = 99999999

        self.quest._upgrade_equipment(process_message=self.quest.quests_stack[-1].process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertTrue(self.hero.money > 0)
