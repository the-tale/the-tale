# coding: utf-8
import mock
import datetime

from questgen import facts

from dext.utils import s11n

from the_tale.common.utils import testcase

from the_tale.common.utils.fake import FakeWorkerCommand

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.actions.prototypes import ActionQuestPrototype

from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.relations import ARTIFACT_TYPE
from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.quests.logic import create_random_quest_for_hero
from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests import uids


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

    def test_do_step(self):
        self.hero.quests.updated = False
        self.quest.process()
        self.assertTrue(self.hero.quests.updated)

    def complete_quest(self, callback=lambda : None):
        current_time = TimePrototype.get_current_time()

        # save link to quest, since it will be removed from hero when quest finished
        quest = self.hero.quests.current_quest

        old_quests_done = self.hero.statistics.quests_done

        while not self.action_idl.leader:
            self.storage.process_turn()
            callback()
            current_time.increment_turn()

        self.assertTrue(isinstance(quest.knowledge_base[quest.machine.pointer.state], facts.Finish))
        self.assertTrue(all(requirement.check(quest) for requirement in quest.knowledge_base[quest.machine.pointer.state].require))

        self.assertTrue(self.hero.quests.history[quest.knowledge_base.filter(facts.Start).next().type] > 0)

        self.assertTrue(old_quests_done < self.hero.statistics.quests_done)

    def check_ui_info(self):
        s11n.to_json(self.hero.ui_info())

    def test_complete_quest(self):
        self.assertEqual(self.hero.quests.interfered_persons, {})
        self.complete_quest(self.check_ui_info)
        self.assertNotEqual(self.hero.quests.interfered_persons, {})

    @mock.patch('the_tale.game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_fast_account_hero(self):
        fake_cmd = FakeWorkerCommand()

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertFalse(fake_cmd.commands)

    @mock.patch('the_tale.game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_premium_account_hero(self):

        self.hero.is_fast = False
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertTrue(fake_cmd.call_count > 0)

    @mock.patch('the_tale.game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertEqual(fake_cmd.call_count, 0)

    def test_power_on_end_quest__give_power_called(self):

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._give_power') as give_power:
            self.hero.is_fast = False
            self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

            self.assertEqual(self.hero.places_history.history, [])

            with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
                self.complete_quest()

            self.assertTrue(fake_cmd.call_count > 0)

        self.assertTrue(give_power.call_count > 0)

    def test_get_experience_for_quest(self):
        self.assertEqual(self.hero.experience, 0)
        self.complete_quest()
        self.assertTrue(self.hero.experience > 0)

    def test_modify_experience(self):
        self.assertEqual(self.quest.modify_experience(100), 100)

        with mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.get_experience_modifier',
                        mock.Mock(return_value=0.1)) as get_experience_modifier:
            self.assertTrue(self.quest.modify_experience(100) > 100)

        self.assertTrue(get_experience_modifier.call_count > 0)

    @mock.patch('the_tale.game.balance.formulas.artifacts_per_battle', lambda *argv: 0)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_get_artifact_for_quest', lambda *argv: False)
    def test_get_money_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertTrue(self.hero.statistics.money_earned_from_quests > 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

    @mock.patch('the_tale.game.balance.formulas.artifacts_per_battle', lambda *argv: 0)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_get_artifact_for_quest', lambda *argv: True)
    def test_get_artifacts_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    def test_get_upgrdade_choice__no_preference(self):
        for i in xrange(100):
            self.assertEqual(self.quest._get_upgrdade_choice(self.hero), 'buy')

    def test_get_upgrdade_choice(self):
        from the_tale.game.heroes.relations import EQUIPMENT_SLOT

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)

        choices = set()

        for i in xrange(100):
            choices.add(self.quest._get_upgrdade_choice(self.hero))

        self.assertEqual(choices, set(('buy', 'sharp')))


    def test_get_upgrdade_choice__no_item_equipped(self):
        from the_tale.game.heroes.relations import EQUIPMENT_SLOT

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.RING)

        for i in xrange(100):
            self.assertEqual(self.quest._get_upgrdade_choice(self.hero), 'buy')


    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: 'buy'))
    def test_upgrade_equipment__buy(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.quest._upgrade_equipment(process_message=self.quest.quests_stack[-1].process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: 'sharp'))
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


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_get_artifact_for_quest', lambda hero: True)
    @mock.patch('the_tale.game.balance.constants.ARTIFACT_POWER_DELTA', 0.0)
    def test_give_reward__artifact_scale(self):

        self.assertEqual(self.hero.bag.occupation, 0)

        ArtifactRecordPrototype.create_random('just_ring', type_=ARTIFACT_TYPE.RING)
        ArtifactRecordPrototype.create_random('just_amulet', type_=ARTIFACT_TYPE.AMULET)

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.buy_artifact_choices',
                        lambda *argv, **kwargs: artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.RING])):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.0)

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.buy_artifact_choices',
                        lambda *argv, **kwargs: artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.AMULET])):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

        self.assertEqual(self.hero.bag.occupation, 2)

        artifact_1, artifact_2 = list(self.hero.bag.values())

        self.assertEqual(abs(artifact_1.power - artifact_2.power), int(c.POWER_TO_LVL * 0.5))

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_get_artifact_for_quest', lambda hero: False)
    @mock.patch('the_tale.game.balance.constants.PRICE_DELTA', 0.0)
    def test_give_reward__money_scale(self):

        self.assertEqual(self.hero.money, 0)

        self.quest._give_reward(self.hero, 'bla-bla', scale=1.0)

        not_scaled_money = self.hero.money

        self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

        self.assertEqual(self.hero.money - not_scaled_money, int(1 + f.sell_artifact_price(self.hero.level) * 1.5))


    def test_all_callbacks_exists(self):
        from questgen.logic import get_required_interpreter_methods
        for method_name in get_required_interpreter_methods():
            self.assertTrue(hasattr(self.quest, method_name))
