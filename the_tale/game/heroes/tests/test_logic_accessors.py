# coding: utf-8
import contextlib

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.balance import constants as c

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.relations import RARITY

from the_tale.game.heroes.conf import heroes_settings
from the_tale.game.heroes import relations


class HeroLogicAccessorsTestBase(testcase.TestCase):

    def setUp(self):
        super(HeroLogicAccessorsTestBase, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]


class HeroLogicAccessorsTest(HeroLogicAccessorsTestBase):

    def check_can_process_turn(self, expected_result, banned=False, bot=False, active=False, premium=False, single=True, idle=False, sinchronized_turn=True):

        if sinchronized_turn:
            turn_number = 6 * heroes_settings.INACTIVE_HERO_DELAY + self.hero.id
        else:
            turn_number = 6 * heroes_settings.INACTIVE_HERO_DELAY + self.hero.id + 1

        with contextlib.nested(
                mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_banned', banned),
                mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_bot', bot),
                mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_active', active),
                mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.is_premium', premium),
                mock.patch('the_tale.game.actions.container.ActionsContainer.is_single', single),
                mock.patch('the_tale.game.actions.container.ActionsContainer.number', 1 if idle else 2)):
            self.assertEqual(self.hero.can_process_turn(turn_number), expected_result)


    def test_can_process_turn__banned(self):
        self.check_can_process_turn(True, banned=True)
        self.check_can_process_turn(False, banned=True, idle=True)
        self.check_can_process_turn(True, active=True)
        self.check_can_process_turn(True, premium=True)
        self.check_can_process_turn(True, single=False)
        self.check_can_process_turn(True, sinchronized_turn=True)
        self.check_can_process_turn(False, sinchronized_turn=False)


    def test_prefered_quest_markers__no_markers(self):
        self.assertTrue(self.hero.habit_honor.interval.is_NEUTRAL)
        self.assertTrue(self.hero.habit_peacefulness.interval.is_NEUTRAL)

        markers = set()

        for i in xrange(1000):
            markers |= self.hero.prefered_quest_markers()

        self.assertEqual(markers, set())


    def test_prefered_quest_markers__has_markers(self):
        from questgen.relations import OPTION_MARKERS

        self.hero.habit_honor.change(500)
        self.hero.habit_peacefulness.change(500)

        self.assertTrue(self.hero.habit_honor.interval.is_RIGHT_2)
        self.assertTrue(self.hero.habit_peacefulness.interval.is_RIGHT_2)

        markers = set()

        for i in xrange(1000):
            markers |= self.hero.prefered_quest_markers()

        self.hero.habit_honor.change(-1000)
        self.hero.habit_peacefulness.change(-1000)

        self.assertTrue(self.hero.habit_honor.interval.is_LEFT_2)
        self.assertTrue(self.hero.habit_peacefulness.interval.is_LEFT_2)

        for i in xrange(1000):
            markers |= self.hero.prefered_quest_markers()

        self.assertEqual(markers, set([OPTION_MARKERS.HONORABLE,
                                       OPTION_MARKERS.DISHONORABLE,
                                       OPTION_MARKERS.AGGRESSIVE,
                                       OPTION_MARKERS.UNAGGRESSIVE]))

    def test_can_safe_artifact_integrity(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.preferences.set_favorite_item(None)
        self.assertFalse(any(self.hero.can_safe_artifact_integrity(artifact) for i in xrange(100)))

    def test_can_safe_artifact_integrity__favorite_item(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)
        self.hero.preferences.set_favorite_item(artifact.type.equipment_slot)
        self.assertTrue(any(self.hero.can_safe_artifact_integrity(artifact) for i in xrange(100)))

    def test_can_safe_artifact_integrity__favorite_item__wrong_slot(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL)

        wrong_slot = None
        for slot in relations.EQUIPMENT_SLOT.records:
            if artifact.type.equipment_slot != slot:
                wrong_slot = slot
                break

        self.hero.preferences.set_favorite_item(wrong_slot)
        self.assertFalse(any(self.hero.can_safe_artifact_integrity(artifact) for i in xrange(100)))

    def test_update_context(self):
        additional_ability = mock.Mock()
        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.abilities') as abilities:
            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.additional_abilities', [additional_ability, additional_ability]):
                with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.habit_honor') as honor:
                    with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.habit_peacefulness') as peacefulness:
                        self.hero.update_context(mock.Mock(), mock.Mock())

        self.assertEqual(abilities.update_context.call_count, 1)
        self.assertEqual(additional_ability.update_context.call_count, 2)
        self.assertEqual(honor.update_context.call_count, 1)
        self.assertEqual(peacefulness.update_context.call_count, 1)


    def test_prefered_mob_loot_multiplier(self):
        from the_tale.game.mobs.storage import mobs_storage

        self.hero._model.level = relations.PREFERENCE_TYPE.MOB.level_required
        self.hero._model.save()

        self.mob = mobs_storage.get_available_mobs_list(level=self.hero.level)[0].create_mob(self.hero)

        self.assertEqual(self.hero.preferences.mob, None)

        with self.check_increased(lambda: self.hero.loot_probability(self.mob)):
            with self.check_increased(lambda: self.hero.artifacts_probability(self.mob)):
                self.hero.preferences.set_mob(self.mob.record)

    def test_companion_damage__delayed_processing(self):
        self.assertTrue(self.hero.real_time_processing)

        normal_damage = self.hero.companion_damage

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.real_time_processing', False):
            self.assertTrue(normal_damage < self.hero.companion_damage)

    def test_companion_damage__bonus_damage(self):
        with mock.patch('the_tale.game.balance.constants.COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS', c.COMPANIONS_WOUNDS_IN_HOUR):
            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.attribute_modifier', lambda s, t: 666 if t.is_COMPANION_DAMAGE else 0):
                for i in xrange(1000):
                    self.assertEqual(self.hero.companion_damage, c.COMPANIONS_DAMAGE_PER_WOUND + 666)


    def test_companion_damage__bonus_damage__damage_from_heal(self):
        with mock.patch('the_tale.game.balance.constants.COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS', 0):
            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.attribute_modifier', lambda s, t: 666 if t.is_COMPANION_DAMAGE else t.default()):
                for i in xrange(1000):
                    self.assertEqual(self.hero.companion_damage, c.COMPANIONS_DAMAGE_PER_WOUND)


    def test_companion_damage_probability(self):
        self.assertEqual(self.hero.companion_damage_probability, c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_HEAL + c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_WOUNDS)

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.attribute_modifier', lambda s, t: 2 if t.is_COMPANION_DAMAGE_PROBABILITY else t.default()):
            self.assertEqual(self.hero.companion_damage_probability, c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_HEAL + 2)
