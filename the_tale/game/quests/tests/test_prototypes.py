# coding: utf-8
import mock
import datetime
import random

from questgen import facts, requirements
from questgen import actions as questgen_actions
from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS
from questgen.relations import OPTION_MARKERS_GROUPS
from questgen.quests.base_quest import RESULTS as QUEST_RESULTS

from dext.common.utils import s11n

from the_tale.common.utils import testcase

from the_tale.common.utils.fake import FakeWorkerCommand

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.prototypes import TimePrototype

from the_tale.game.actions.prototypes import ActionMoveToPrototype, ActionMoveNearPlacePrototype

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage
from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import relations as persons_relations
from the_tale.game.persons import logic as persons_logic
from the_tale.game.persons import models as persons_models

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.actions.prototypes import ActionQuestPrototype

from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.relations import ARTIFACT_TYPE
from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.quests import logic
from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests import exceptions
from the_tale.game.quests import uids
from the_tale.game.quests import relations

from the_tale.game.heroes.relations import HABIT_CHANGE_SOURCE

from the_tale.game.quests.tests import helpers


class PrototypeTestsBase(testcase.TestCase):

    def setUp(self):
        super(PrototypeTestsBase, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.action_idl = self.hero.actions.current_action

        self.action_idl.state = self.action_idl.STATE.QUEST

        self.action_quest = ActionQuestPrototype.create(hero=self.hero)
        helpers.setup_quest(self.hero)

        self.quest = self.hero.quests.current_quest


class PrototypeTests(PrototypeTestsBase):

    def setUp(self):
        super(PrototypeTests, self).setUp()

    def test_serialization(self):
        self.assertEqual(self.quest.serialize(), QuestPrototype.deserialize(self.quest.serialize()).serialize())

    def test_do_step(self):
        self.hero.quests.updated = False
        self.quest.process()
        self.assertTrue(self.hero.quests.updated)

    def complete_quest(self, callback=lambda : None):
        current_time = TimePrototype.get_current_time()

        # save link to quest, since it will be removed from hero when quest finished
        quest = self.hero.quests.current_quest

        # modify givepower, to give only positive values
        for fact in quest.knowledge_base._facts.values():
            for action in getattr(fact, 'actions', ()):
                if isinstance(action, questgen_actions.GivePower):
                    action.power = 100

        old_quests_done = self.hero.statistics.quests_done

        while not self.action_idl.leader:
            self.hero.health = self.hero.max_health
            self.storage.process_turn()
            callback()
            current_time.increment_turn()

        self.assertTrue(isinstance(quest.knowledge_base[quest.machine.pointer.state], facts.Finish))

        self.assertTrue(all(requirement.check(quest) for requirement in quest.knowledge_base[quest.machine.pointer.state].require))

        self.assertTrue(self.hero.quests.history[quest.knowledge_base.filter(facts.Start).next().type] > 0)

        self.assertTrue(old_quests_done < self.hero.statistics.quests_done)

    def check_ui_info(self):
        s11n.to_json(self.hero.ui_info(actual_guaranteed=True))

    def test_complete_quest(self):
        self.assertEqual(self.hero.quests.interfered_persons, {})
        self.complete_quest(self.check_ui_info)
        self.assertNotEqual(self.hero.quests.interfered_persons, {})


    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_person_power', lambda self, person: True)
    def test_give_person_power__profession(self):

        person = persons_storage.persons_storage.all()[0]

        power_without_profession = self.quest._give_person_power(self.hero, person, 1.0)

        self.quest.knowledge_base += facts.ProfessionMarker(person=uids.person(person.id), profession=666)
        power_with_profession = self.quest._give_person_power(self.hero, person, 1.0)

        self.assertTrue(power_with_profession < power_without_profession)


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


    @mock.patch('the_tale.game.quests.prototypes.QuestInfo.get_person_power_for_quest', classmethod(lambda cls, hero: 1))
    def test_power_on_end_quest_for_normal_account_hero__in_frontier(self):

        for place in places_storage.all():
            place._model.is_frontier = True

        self.hero.is_fast = False

        self.assertEqual(self.hero.places_history.history, [])

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as fake_cmd:
            self.complete_quest()

        self.assertTrue(len(self.hero.places_history.history) > 0)

        self.assertTrue(fake_cmd.call_count > 0)

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

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda *argv: False)
    def test_get_money_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertTrue(self.hero.statistics.money_earned_from_quests > 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda *argv: True)
    def test_get_artifacts_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    def test_get_upgrdade_choice__no_preference(self):
        for i in xrange(100):
            self.assertTrue(self.quest._get_upgrdade_choice(self.hero).is_BUY)

    def test_get_upgrdade_choice(self):
        from the_tale.game.heroes.relations import EQUIPMENT_SLOT

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.equipment.get(EQUIPMENT_SLOT.PLATE).integrity = 0

        choices = set()

        for i in xrange(100):
            choices.add(self.quest._get_upgrdade_choice(self.hero))

        self.assertEqual(choices, set((relations.UPGRADE_EQUIPMENT_VARIANTS.BUY,
                                       relations.UPGRADE_EQUIPMENT_VARIANTS.SHARP,
                                       relations.UPGRADE_EQUIPMENT_VARIANTS.REPAIR)))


    def test_get_upgrdade_choice__no_item_equipped(self):
        from the_tale.game.heroes.relations import EQUIPMENT_SLOT

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.RING)

        for i in xrange(100):
            self.assertTrue(self.quest._get_upgrdade_choice(self.hero).is_BUY)


    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: relations.UPGRADE_EQUIPMENT_VARIANTS.BUY))
    def test_upgrade_equipment__buy(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: relations.UPGRADE_EQUIPMENT_VARIANTS.SHARP))
    def test_upgrade_equipment__sharp(self):
        old_power = self.hero.power.clone()
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(old_power.total() + 1, self.hero.power.total())

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: relations.UPGRADE_EQUIPMENT_VARIANTS.REPAIR))
    def test_upgrade_equipment__repair(self):

        test_artifact = random.choice(self.hero.equipment.values())
        test_artifact.integrity = 0
        self.hero.preferences.set_equipment_slot(test_artifact.type.equipment_slot)

        old_power = self.hero.power.clone()
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(old_power.total(), self.hero.power.total())
        self.assertEqual(test_artifact.integrity, test_artifact.max_integrity)

    def test_upgrade_equipment__money_limit(self):
        self.hero.money = 99999999

        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertTrue(self.hero.money > 0)


    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda hero: True)
    @mock.patch('the_tale.game.balance.constants.ARTIFACT_POWER_DELTA', 0.0)
    def test_give_reward__artifact_scale(self):

        self.assertEqual(self.hero.bag.occupation, 0)

        ArtifactRecordPrototype.create_random('just_ring', type_=ARTIFACT_TYPE.RING)
        ArtifactRecordPrototype.create_random('just_amulet', type_=ARTIFACT_TYPE.AMULET)

        with mock.patch('the_tale.game.heroes.objects.Hero.receive_artifacts_choices',
                        lambda *argv, **kwargs: artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.RING])):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.0)

        with mock.patch('the_tale.game.heroes.objects.Hero.receive_artifacts_choices',
                        lambda *argv, **kwargs: artifacts_storage.artifacts_for_type([ARTIFACT_TYPE.AMULET])):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

        self.assertEqual(self.hero.bag.occupation, 2)

        artifact_1, artifact_2 = sorted(self.hero.bag.values(), key=lambda artifact: artifact.bag_uuid)

        self.assertEqual(artifact_1.level + 1, artifact_2.level)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda hero: False)
    def test_give_reward__money_scale(self):

        self.assertEqual(self.hero.money, 0)

        self.quest._give_reward(self.hero, 'bla-bla', scale=1.0)

        not_scaled_money = self.hero.money

        self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

        self.assertEqual(self.hero.money - not_scaled_money, int(f.sell_artifact_price(self.hero.level) * 1.5))

    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda hero: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.quest_money_reward_multiplier', lambda hero: -100)
    def test_give_reward__money_scale_less_then_zero(self):

        with self.check_delta(lambda: self.hero.money, 1):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

    def test_give_social_power(self):
        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        for person in persons_storage.persons_storage.all():
            person_uid = uids.person(person.id)
            if person_uid not in self.quest.knowledge_base:
                self.quest.knowledge_base += logic.fact_person(person)

        person_1_1 =  self.place_3.persons[0]
        person_1_2 =  self.place_3.persons[1]
        person_1_3 =  self.place_3.persons[2]
        person_2_1 =  self.place_2.persons[0]
        person_2_2 =  self.place_2.persons[1]
        person_2_3 =  self.place_2.persons[2]

        results = {uids.person(person_1_1.id): QUEST_RESULTS.SUCCESSED,
                   uids.person(person_1_2.id): QUEST_RESULTS.FAILED,
                   uids.person(person_1_3.id): QUEST_RESULTS.NEUTRAL,
                   uids.person(person_2_1.id): QUEST_RESULTS.SUCCESSED,
                   uids.person(person_2_2.id): QUEST_RESULTS.FAILED,
                   uids.person(person_2_3.id): QUEST_RESULTS.NEUTRAL}

        persons_models.SocialConnection.objects.all().delete()
        persons_storage.social_connections.refresh()
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_1, person_2_1)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_1, person_2_2)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_1, person_2_3)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_2, person_2_2)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_2, person_2_3)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_3, person_2_3)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._give_person_power') as give_person_power:
            self.quest.give_social_power(results)

        calls = set((call[1]['person'].id, call[1]['power'])
                    for call in give_person_power.call_args_list)

        self.assertEqual(calls,
                         set(((person_1_1.id, 1),
                              (person_2_1.id, 1),
                              (person_1_2.id, -1),
                              (person_2_2.id, -1))))

        persons_models.SocialConnection.objects.all().delete()
        persons_storage.social_connections.refresh()
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, person_1_1, person_2_1)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, person_1_1, person_2_2)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, person_1_1, person_2_3)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, person_1_2, person_2_2)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, person_1_2, person_2_3)
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, person_1_3, person_2_3)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._give_person_power') as give_person_power:
            self.quest.give_social_power(results)

        calls = set((call[1]['person'].id, call[1]['power'])
                    for call in give_person_power.call_args_list)

        self.assertEqual(calls,
                         set(((person_1_1.id, 1),
                              (person_2_2.id, -1))))

    def test_give_social_power__two_results(self):
        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        for person in persons_storage.persons_storage.all():
            person_uid = uids.person(person.id)
            if person_uid not in self.quest.knowledge_base:
                self.quest.knowledge_base += logic.fact_person(person)

        person_1_1 =  self.place_3.persons[0]
        person_2_1 =  self.place_2.persons[0]

        results = {uids.person(person_1_1.id): QUEST_RESULTS.SUCCESSED,
                   uids.person(person_2_1.id): QUEST_RESULTS.SUCCESSED}

        persons_models.SocialConnection.objects.all().delete()
        persons_storage.social_connections.refresh()
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER, person_1_1, person_2_1)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._give_person_power') as give_person_power:
            self.quest.give_social_power(results)

        calls = set((call[1]['person'].id, call[1]['power'])
                    for call in give_person_power.call_args_list)

        self.assertEqual(calls,
                         set(((person_1_1.id, 1),
                              (person_2_1.id, 1))))


    def test_give_social_power__one_result(self):
        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        for person in persons_storage.persons_storage.all():
            person_uid = uids.person(person.id)
            if person_uid not in self.quest.knowledge_base:
                self.quest.knowledge_base += logic.fact_person(person)

        person_1_1 =  self.place_3.persons[0]

        results = {uids.person(person_1_1.id): QUEST_RESULTS.SUCCESSED}

        persons_models.SocialConnection.objects.all().delete()
        persons_storage.social_connections.refresh()

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._give_person_power') as give_person_power:
            self.quest.give_social_power(results)

        calls = set((call[1]['person'].id, call[1]['power'])
                    for call in give_person_power.call_args_list)

        self.assertEqual(calls, set())


    def test_give_social_power__no_results(self):
        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        for person in persons_storage.persons_storage.all():
            person_uid = uids.person(person.id)
            if person_uid not in self.quest.knowledge_base:
                self.quest.knowledge_base += logic.fact_person(person)

        results = {}

        persons_models.SocialConnection.objects.all().delete()
        persons_storage.social_connections.refresh()

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._give_person_power') as give_person_power:
            self.quest.give_social_power(results)

        calls = set((call[1]['person'].id, call[1]['power'])
                    for call in give_person_power.call_args_list)

        self.assertEqual(calls, set())



    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.modify_experience', lambda self, exp: exp)
    @mock.patch('the_tale.game.heroes.objects.Hero.experience_modifier', 2)
    def test_finish_quest__add_bonus_experience(self):

        self.quest.current_info.experience = 10
        self.quest.current_info.experience_bonus = 1

        # we don't modify power bonus like main power, becouse of possible experience_modifier < 1
        with self.check_delta(lambda: self.hero.experience, 21):
            self.quest._finish_quest(mock.Mock(results=mock.Mock(iteritems=lambda: [])), self.hero)

    def test_finish_quest__add_companion_experience(self):
        from the_tale.game.companions import storage as companions_storage
        from the_tale.game.companions import logic as companions_logic

        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)
        companion.coherence = 50

        self.hero.set_companion(companion)

        with self.check_increased(lambda: self.hero.companion.experience):
            with self.check_not_changed(lambda: self.hero.companion.coherence):
                self.quest._finish_quest(mock.Mock(results=mock.Mock(iteritems=lambda: [])), self.hero)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_give_power__add_bonus_power(self):

        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        # we modify power bonus like main power
        self.assertEqual(self.quest._give_power(self.hero, self.place_1, 2), 22)


class InterpreterCallbacksTests(PrototypeTestsBase):

    def setUp(self):
        super(InterpreterCallbacksTests, self).setUp()

    def test_all_callbacks_exists(self):
        from questgen.logic import get_required_interpreter_methods
        for method_name in get_required_interpreter_methods():
            self.assertTrue(hasattr(self.quest, method_name))

    def test_on_jump_end__only_one_marker_from_group(self):
        all_markers = {}
        for group in OPTION_MARKERS_GROUPS:
            for marker in group:
                all_markers[marker] = random.choice([True, False])

        self.quest.current_info.used_markers = all_markers

        self.assertEqual(set(self.quest.current_info.used_markers.keys()), set([QUEST_OPTION_MARKERS.HONORABLE,
                                                                                    QUEST_OPTION_MARKERS.DISHONORABLE,
                                                                                    QUEST_OPTION_MARKERS.AGGRESSIVE,
                                                                                    QUEST_OPTION_MARKERS.UNAGGRESSIVE]))

        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[QUEST_OPTION_MARKERS.HONORABLE, QUEST_OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)

        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        self.assertEqual(set(self.quest.current_info.used_markers.keys()), set([QUEST_OPTION_MARKERS.HONORABLE, QUEST_OPTION_MARKERS.AGGRESSIVE]))

    def test_update_habits__on_jump_end__after_actions__no_markers__default(self):
        jump = facts.Jump(state_from='state_from', state_to='state_to')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions__wrong_markers__default(self):
        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[666, 75], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions__default(self):
        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[QUEST_OPTION_MARKERS.HONORABLE, QUEST_OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        self.assertEqual(self.quest.current_info.used_markers,
                         {QUEST_OPTION_MARKERS.HONORABLE: True,
                          QUEST_OPTION_MARKERS.AGGRESSIVE: True})

    def test_finish_quest__update_habits__defaults(self):
        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[QUEST_OPTION_MARKERS.HONORABLE, QUEST_OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_state__after_actions(facts.Finish(uid='test_uid',
                                                            start='any_start_uid',
                                                            results={},
                                                            nesting=666))

        self.assertEqual(update_habits.call_args_list, [mock.call(HABIT_CHANGE_SOURCE.QUEST_HONORABLE_DEFAULT),
                                                        mock.call(HABIT_CHANGE_SOURCE.QUEST_AGGRESSIVE_DEFAULT)])



    def test_update_habits__on_jump_end__after_actions__no_markers(self):
        jump = facts.Jump(state_from='state_from', state_to='state_to')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions__wrong_markers(self):
        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[666, 75], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions(self):
        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[QUEST_OPTION_MARKERS.HONORABLE, QUEST_OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        self.assertEqual(self.quest.current_info.used_markers,
                         {QUEST_OPTION_MARKERS.HONORABLE: False,
                          QUEST_OPTION_MARKERS.AGGRESSIVE: False})

    def test_finish_quest__update_habits__custom(self):

        jump = facts.Option(state_from='state_from', state_to='state_to', markers=[QUEST_OPTION_MARKERS.HONORABLE, QUEST_OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_state__after_actions(facts.Finish(uid='test_uid',
                                                            start='any_start_uid',
                                                            results={},
                                                            nesting=666))

        self.assertEqual(update_habits.call_args_list, [mock.call(HABIT_CHANGE_SOURCE.QUEST_HONORABLE),
                                                        mock.call(HABIT_CHANGE_SOURCE.QUEST_AGGRESSIVE)])


class CheckRequirementsTests(PrototypeTestsBase):

    def setUp(self):
        super(CheckRequirementsTests, self).setUp()

        self.hero_fact = self.quest.knowledge_base.filter(facts.Hero).next()
        self.person_fact = self.quest.knowledge_base.filter(facts.Person).next()

        self.person = persons_storage.persons_storage[self.person_fact.externals['id']]

        self.place_1_fact = facts.Place(uid='place_1', externals={'id': self.place_1.id})
        self.place_2_fact = facts.Place(uid='place_2', externals={'id': self.place_2.id})
        self.place_3_fact = facts.Place(uid='place_3', externals={'id': self.place_3.id})

        self.quest.knowledge_base += [self.place_1_fact, self.place_2_fact, self.place_3_fact]


    def get_check_places(self, place_id):
        for place in self.quest.knowledge_base.filter(facts.Place):
            if places_storage[place.externals['id']].id == place_id:
                place_fact = place
                break

        for place in self.quest.knowledge_base.filter(facts.Place):
            if places_storage[place.externals['id']].id != place_id:
                non_place_fact = place
                break

        return place_fact, non_place_fact

    # located in

    def check_located_in(self, object, place, result):
        requirement = requirements.LocatedIn(object=object.uid, place=place.uid)
        self.assertEqual(self.quest.check_located_in(requirement), result)

    def test_check_located_in__person(self):
        person_place_fact, nonperson_place_fact = self.get_check_places(self.person.place_id)

        self.check_located_in(object=self.person_fact, place=person_place_fact, result=True)
        self.check_located_in(object=self.person_fact, place=nonperson_place_fact, result=False)

    def test_check_located_in__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero
        self.check_located_in(object=wrong_hero, place=self.quest.knowledge_base.filter(facts.Place).next(), result=False)

    def test_check_located_in__hero__in_place(self):
        self.hero.position.set_place(self.place_1)

        self.check_located_in(object=self.hero_fact, place=self.place_1_fact, result=True)
        self.check_located_in(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_in__hero__move_near(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.check_located_in(object=self.hero_fact, place=self.place_1_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_in__hero__road(self):
        self.hero.position.set_road(roads_storage.get_by_places(self.place_1, self.place_2), percents=0.5)

        self.check_located_in(object=self.hero_fact, place=self.place_1_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_in__wrong_requirement(self):
        place_uid = self.quest.knowledge_base.filter(facts.Place).next().uid
        requirement = requirements.LocatedIn(object=place_uid, place=place_uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_located_in, requirement)

    # located near

    def check_located_near(self, object, place, result):
        requirement = requirements.LocatedNear(object=object.uid, place=place.uid)
        self.assertEqual(self.quest.check_located_near(requirement), result)

    def test_check_located_near__person(self):
        person_place_fact, nonperson_place_fact = self.get_check_places(self.person.place_id)

        self.check_located_near(object=self.person_fact, place=person_place_fact, result=False)
        self.check_located_near(object=self.person_fact, place=nonperson_place_fact, result=False)

    def test_check_located_near__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero
        self.check_located_near(object=wrong_hero, place=self.quest.knowledge_base.filter(facts.Place).next(), result=False)

    def test_check_located_near__hero__in_place(self):
        self.hero.position.set_place(self.place_1)

        self.check_located_near(object=self.hero_fact, place=self.place_1_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_near__hero__move_near(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.check_located_near(object=self.hero_fact, place=self.place_1_fact, result=True)
        self.check_located_near(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_near__hero__road(self):
        self.hero.position.set_road(roads_storage.get_by_places(self.place_1, self.place_2), percents=0.25)

        self.check_located_near(object=self.hero_fact, place=self.place_1_fact, result=True)
        self.check_located_near(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_near__wrong_requirement(self):
        place_uid = self.quest.knowledge_base.filter(facts.Place).next().uid
        requirement = requirements.LocatedNear(object=place_uid, place=place_uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_located_near, requirement)


    # located on road

    def check_located_on_road(self, object, place_from, place_to, percents, result):
        requirement = requirements.LocatedOnRoad(object=object.uid, place_from=place_from.uid, place_to=place_to.uid, percents=percents)
        self.assertEqual(self.quest.check_located_on_road(requirement), result)

    def test_check_located_on_road__person(self):
        person_place_fact, nonperson_place_fact = self.get_check_places(self.person.place_id)

        self.check_located_on_road(object=self.person_fact, place_from=person_place_fact, place_to=nonperson_place_fact, percents=0.01, result=False)
        self.check_located_on_road(object=self.person_fact, place_from=person_place_fact, place_to=nonperson_place_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.person_fact, place_from=nonperson_place_fact, place_to=person_place_fact, percents=0.01, result=False)
        self.check_located_on_road(object=self.person_fact, place_from=nonperson_place_fact, place_to=person_place_fact, percents=0.99, result=False)

    def test_check_located_on_road__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        self.check_located_on_road(object=wrong_hero, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.01, result=False)
        self.check_located_on_road(object=wrong_hero, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=wrong_hero, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.01, result=False)
        self.check_located_on_road(object=wrong_hero, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=False)

    def test_check_located_on_road__hero__in_place(self):
        self.hero.position.set_place(self.place_1)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=1, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=1, result=True)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.01, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.01, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=True)

    def test_check_located_on_road__hero__move_near(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.01, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.01, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=False)

    def test_check_located_on_road__hero__road(self):
        self.hero.position.set_road(roads_storage.get_by_places(self.place_1, self.place_2), percents=0.25)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.01, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.01, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=False)

    def test_check_located_on_road__wrong_requirement(self):
        requirement = requirements.LocatedOnRoad(object=self.place_1_fact.uid, place_from=self.place_2_fact.uid, place_to=self.place_3_fact.uid, percents=0.25)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_located_on_road, requirement)

    # has money

    def test_check_has_money__person(self):
        requirement = requirements.HasMoney(object=self.person_fact.uid, money=666)
        self.assertFalse(self.quest.check_has_money(requirement))

    def test_check_has_money__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.HasMoney(object=wrong_hero.uid, money=666)
        self.assertFalse(self.quest.check_has_money(requirement))

    def test_check_has_money__hero(self):
        requirement = requirements.HasMoney(object=self.hero_fact.uid, money=666)
        self.assertFalse(self.quest.check_has_money(requirement))

        self.hero.money = 667
        self.assertTrue(self.quest.check_has_money(requirement))

    def test_check_has_money__wrong_requirement(self):
        requirement = requirements.HasMoney(object=self.place_1_fact.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_has_money, requirement)

    # is alive

    def test_check_is_alive__person(self):
        requirement = requirements.IsAlive(object=self.person_fact.uid)
        self.assertTrue(self.quest.check_is_alive(requirement))

    def test_check_is_alive__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.IsAlive(object=wrong_hero.uid)
        self.assertFalse(self.quest.check_is_alive(requirement))

    def test_check_is_alive__hero(self):
        requirement = requirements.IsAlive(object=self.hero_fact.uid)
        self.assertTrue(self.quest.check_is_alive(requirement))

        self.hero.kill()
        self.assertFalse(self.quest.check_is_alive(requirement))

    def test_check_is_alive__wrong_requirement(self):
        requirement = requirements.IsAlive(object=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_is_alive, requirement)



class SatisfyRequirementsTests(PrototypeTestsBase):

    def setUp(self):
        super(SatisfyRequirementsTests, self).setUp()

        self.hero_fact = self.quest.knowledge_base.filter(facts.Hero).next()
        self.person_fact = self.quest.knowledge_base.filter(facts.Person).next()

        self.person = persons_storage.persons_storage[self.person_fact.externals['id']]

        self.place_1_fact = facts.Place(uid='place_1', externals={'id': self.place_1.id})
        self.place_2_fact = facts.Place(uid='place_2', externals={'id': self.place_2.id})
        self.place_3_fact = facts.Place(uid='place_3', externals={'id': self.place_3.id})

        self.quest.knowledge_base += [self.place_1_fact, self.place_2_fact, self.place_3_fact]


    def get_check_places(self, place_id):
        for place in self.quest.knowledge_base.filter(facts.Place):
            if places_storage[place.externals['id']].id == place_id:
                place_fact = place
                break

        for place in self.quest.knowledge_base.filter(facts.Place):
            if places_storage[place.externals['id']].id != place_id:
                non_place_fact = place
                break

        return place_fact, non_place_fact

    # located in

    def test_satisfy_located_in__non_hero(self):
        requirement = requirements.LocatedIn(object=self.person_fact.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_in, requirement)

    def test_satisfy_located_in__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.LocatedIn(object=wrong_hero.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_in, requirement)

    def test_satisfy_located_in__success(self):
        self.hero.position.set_place(self.place_1)

        requirement = requirements.LocatedIn(object=self.hero_fact.uid, place=self.place_2_fact.uid)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_to') as move_hero_to:
            self.quest.satisfy_located_in(requirement)

        self.assertEqual(move_hero_to.call_args_list, [mock.call(destination=self.place_2)])

    # located near

    def test_satisfy_located_near__non_hero(self):
        requirement = requirements.LocatedNear(object=self.person_fact.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_near, requirement)

    def test_satisfy_located_near__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.LocatedNear(object=wrong_hero.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_near, requirement)

    def test_satisfy_located_near__success(self):
        requirement = requirements.LocatedNear(object=self.hero_fact.uid, place=self.place_2_fact.uid, terrains=[1, 2])

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_near') as move_hero_near:
            self.quest.satisfy_located_near(requirement)

        self.assertEqual(move_hero_near.call_args_list, [mock.call(destination=self.place_2, terrains=[1, 2])])


    def test_satisfy_located_near__no_place(self):
        requirement = requirements.LocatedNear(object=self.hero_fact.uid, place=None, terrains=[1, 2])

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_near') as move_hero_near:
            self.quest.satisfy_located_near(requirement)

        self.assertEqual(move_hero_near.call_args_list, [mock.call(destination=None, terrains=[1, 2])])


    # located on road

    def test_satisfy_located_on_road__non_hero(self):
        requirement = requirements.LocatedOnRoad(object=self.person_fact.uid, place_from=self.place_1_fact.uid, place_to=self.place_2_fact.uid, percents=0.5)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_on_road, requirement)

    def test_satisfy_located_on_road__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.LocatedOnRoad(object=wrong_hero.uid, place_from=self.place_1_fact.uid, place_to=self.place_2_fact.uid, percents=0.5)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_on_road, requirement)

    def test_satisfy_located_on_road__success(self):
        requirement = requirements.LocatedOnRoad(object=self.hero_fact.uid, place_from=self.place_1_fact.uid, place_to=self.place_2_fact.uid, percents=0.5)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_on_road') as move_hero_on_road:
            self.quest.satisfy_located_on_road(requirement)

        self.assertEqual(move_hero_on_road.call_args_list, [mock.call(place_from=self.place_1,
                                                                      place_to=self.place_2,
                                                                      percents=0.5)])

    # located has money

    def test_satisfy_has_money__non_hero(self):
        requirement = requirements.HasMoney(object=self.person_fact.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_has_money, requirement)

    def test_satisfy_has_money__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.HasMoney(object=wrong_hero.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_has_money, requirement)

    def test_satisfy_has_money__success(self):
        requirement = requirements.HasMoney(object=self.hero_fact.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_has_money, requirement)

    # located is alive

    def test_satisfy_is_alive__non_hero(self):
        requirement = requirements.IsAlive(object=self.person_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_is_alive, requirement)

    def test_satisfy_is_alive__wrong_hero(self):
        wrong_hero = facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = requirements.IsAlive(object=wrong_hero.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_is_alive, requirement)

    def test_satisfy_is_alive__success(self):
        requirement = requirements.IsAlive(object=self.hero_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_is_alive, requirement)


class PrototypeMoveHeroTests(PrototypeTestsBase):

    def setUp(self):
        super(PrototypeMoveHeroTests, self).setUp()

    # move hero to

    def test_move_hero_to__from_walking(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.quest._move_hero_to(self.place_1)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveNearPlacePrototype))
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)

    def test_move_hero_to__from_road(self):
        self.hero.position.set_road(roads_storage.get_by_places(self.place_1, self.place_2), percents=0.5)

        self.quest._move_hero_to(self.place_3)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveToPrototype))
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.break_at, None)

    def test_move_hero_to__from_place(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_to(self.place_3)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveToPrototype))
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.break_at, None)

    def test_move_hero_to__break_at(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_to(self.place_3, break_at=0.25)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveToPrototype))
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.break_at, 0.25)


    # move hero to

    def test_move_hero_near__from_walking(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.quest._move_hero_near(self.place_1)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveNearPlacePrototype))
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)
        self.assertFalse(self.hero.actions.current_action.back)

    def test_move_hero_near__from_road(self):
        self.hero.position.set_road(roads_storage.get_by_places(self.place_1, self.place_2), percents=0.5)

        self.quest._move_hero_near(self.place_3)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveNearPlacePrototype))
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_3.id)
        self.assertFalse(self.hero.actions.current_action.back)

    def test_move_hero_near__from_place(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_near(self.place_1)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveNearPlacePrototype))
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)
        self.assertFalse(self.hero.actions.current_action.back)

    def test_move_hero_near__back(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.quest._move_hero_near(self.place_1, back=True)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveNearPlacePrototype))
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)
        self.assertTrue(self.hero.actions.current_action.back)


    # move hero on road

    def test_move_hero_on_road__from_walking(self):
        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x+1,  self.place_1.y+1, percents=0.5)

        self.quest._move_hero_on_road(place_from=self.place_1, place_to=self.place_3, percents=0.9)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveNearPlacePrototype))
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)
        self.assertTrue(self.hero.actions.current_action.back)

    def test_move_hero_on_road__from_road(self):
        self.hero.position.set_road(roads_storage.get_by_places(self.place_1, self.place_2), percents=0.5)

        self.quest._move_hero_on_road(place_from=self.place_1, place_to=self.place_3, percents=0.9)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveToPrototype))
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertTrue(0 < self.hero.actions.current_action.break_at < 0.9)

    def test_move_hero_on_road__from_place(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_on_road(place_from=self.place_1, place_to=self.place_3, percents=0.9)

        self.assertTrue(isinstance(self.hero.actions.current_action, ActionMoveToPrototype))
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(round(self.hero.actions.current_action.break_at, 4), 0.9000)
