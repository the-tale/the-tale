# coding: utf-8
import datetime
import time
import random
import copy

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype, GameState

from the_tale.game.quests.relations import QUESTS

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Damage

from the_tale.game import relations as game_relations

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions.abilities import effects as companions_effects
from the_tale.game.companions.abilities import container as companions_abilities_container

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.places.relations import CITY_MODIFIERS
from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.bills import conf as bills_conf

from ..habilities import ABILITY_TYPE, ABILITIES, battle, ABILITY_AVAILABILITY
from ..conf import heroes_settings
from .. import relations
from .. import messages
from .. import logic
from .. import models
from .. import objects


def get_simple_cache_data(*argv, **kwargs):
    return {'ui_caching_started_at': kwargs.get('ui_caching_started_at', 0),
            'changed_fields': [],
            'pvp__actual': 'x',
            'pvp__last_turn': 'y',
            'patch_turn': None}


class HeroTest(testcase.TestCase):

    def setUp(self):
        super(HeroTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]


    def test_create(self):
        self.assertFalse(self.hero.force_save_required)

        self.assertTrue(self.hero.is_alive)
        self.assertEqual(self.hero.created_at_turn, TimePrototype.get_current_time().turn_number)
        self.assertEqual(self.hero.abilities.get('hit').level, 1)
        self.assertEqual(self.hero.abilities.get('coherence').level, 1)

        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL)

        self.assertEqual(models.HeroPreferences.objects.count(), 1)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).energy_regeneration_type, self.hero.preferences.energy_regeneration_type)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).risk_level, self.hero.preferences.risk_level)

    def test_helps_number_restriction(self):
        self.assertEqual(self.hero.last_help_on_turn, 0)
        self.assertEqual(self.hero.helps_in_turn, 0)

        self.assertTrue(self.hero.can_be_helped())

        for i in xrange(heroes_settings.MAX_HELPS_IN_TURN-1):
            self.hero.on_help()

        self.assertEqual(self.hero.helps_in_turn, heroes_settings.MAX_HELPS_IN_TURN-1)

        self.assertTrue(self.hero.can_be_helped())

        self.hero.on_help()

        self.assertFalse(self.hero.can_be_helped())

        current_turn = TimePrototype.get_current_time()
        current_turn.increment_turn()

        self.assertTrue(self.hero.can_be_helped())

        self.hero.on_help()

        self.assertEqual(self.hero.last_help_on_turn, current_turn.turn_number)
        self.assertEqual(self.hero.helps_in_turn, 1)


    def test_is_premium(self):
        self.assertFalse(self.hero.is_premium)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.assertTrue(self.hero.is_premium)

    def test_is_banned(self):
        self.assertFalse(self.hero.is_banned)
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.assertTrue(self.hero.is_banned)

    def test_is_active(self):
        self.assertTrue(self.hero.is_active)
        self.hero.active_state_end_at = datetime.datetime.now()
        self.assertFalse(self.hero.is_active)

    def test_create_time(self):
        game_time = TimePrototype.get_current_time()
        game_time.increment_turn()
        game_time.increment_turn()
        game_time.increment_turn()
        game_time.save()

        result, account_id, bundle_id = register_user('test_user_2')

        hero = logic.load_hero(account_id=account_id)

        self.assertEqual(hero.created_at_turn, TimePrototype.get_current_time().turn_number)

        self.assertTrue(hero.created_at_turn != self.hero.created_at_turn)

    def test_convert_experience_to_energy__no_experience(self):
        with self.check_not_changed(lambda: self.hero.experience):
            with self.check_not_changed(lambda: self.hero.energy_bonus):
                self.hero.convert_experience_to_energy(10)

    @mock.patch('the_tale.game.heroes.objects.Hero.experience_modifier', 1.0)
    def test_convert_experience_to_energy(self):
        self.hero.add_experience(41)
        self.assertEqual(self.hero.experience, 41)

        with self.check_delta(lambda: self.hero.experience, -41):
            with self.check_delta(lambda: self.hero.energy_bonus, 5):
                self.hero.convert_experience_to_energy(10)

    def test_experience_modifier__banned(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertEqual(self.hero.experience_modifier, 0)

    def test_experience_modifier__risk_level(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.preferences.set_risk_level(relations.RISK_LEVEL.VERY_HIGH)
        self.assertTrue(c.EXP_FOR_NORMAL_ACCOUNT < self.hero.experience_modifier)

        self.hero.preferences.set_risk_level(relations.RISK_LEVEL.VERY_LOW)
        self.assertTrue(c.EXP_FOR_NORMAL_ACCOUNT > self.hero.experience_modifier)

    def test_experience_modifier__active_inactive_state(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)

        # inactive heroes get the same exp, insteed experience penalty  there action delayed
        self.assertTrue(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60),
                                           might=0,
                                           actual_bills=[])

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

    def test_experience_modifier__with_premium(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_PREMIUM_ACCOUNT)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60),
                                           might=666,
                                           actual_bills=[])

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

    def test_can_participate_in_pvp(self):
        self.assertFalse(self.hero.can_participate_in_pvp)

        self.hero.is_fast = False

        self.assertTrue(self.hero.can_participate_in_pvp)
        with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
            self.assertFalse(self.hero.can_participate_in_pvp)

    def test_can_change_person_power(self):
        self.assertFalse(self.hero.can_change_person_power(self.place_1.persons[0]))

    def test_can_change_person_power__premium(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_change_person_power(self.place_1.persons[0]))

    def test_can_change_person_power__depends_from_all_heroes(self):
        with mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.depends_from_all_heroes', True):
            self.assertTrue(self.hero.can_change_person_power(self.place_1.persons[0]))

    def test_can_change_person_power__banned(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        with mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.depends_from_all_heroes', True):
            with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
                self.assertFalse(self.hero.can_change_person_power(self.place_1.persons[0]))


    def test_can_change_place_power(self):
        self.assertFalse(self.hero.can_change_place_power(self.place_1))

    def test_can_change_place_power__premium(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_change_place_power(self.place_1))

    def test_can_change_place_power__depends_from_all_heroes(self):
        with mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.depends_from_all_heroes', True):
            self.assertTrue(self.hero.can_change_place_power(self.place_1))

    def test_can_change_place_power__banned(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        with mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.depends_from_all_heroes', True):
            with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
                self.assertFalse(self.hero.can_change_person_power(self.place_1))

    def test_can_repair_building(self):
        self.assertFalse(self.hero.can_repair_building)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_repair_building)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
            self.assertFalse(self.hero.can_repair_building)

    def test_update_with_account_data(self):
        self.hero.is_fast = True
        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=1)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           might=666,
                                           actual_bills=[7])

        self.assertFalse(self.hero.is_fast)
        self.assertTrue(self.hero.active_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.premium_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.ban_state_end_at > datetime.datetime.now())
        self.assertEqual(self.hero.might, 666)
        self.assertEqual(self.hero.actual_bills, [7])

    def test_reward_modifier__risk_level(self):
        self.assertEqual(self.hero.quest_money_reward_multiplier(), 1.0)
        self.hero.preferences.set_risk_level(relations.RISK_LEVEL.VERY_HIGH)
        self.assertTrue(self.hero.quest_money_reward_multiplier() > 1.0)
        self.hero.preferences.set_risk_level(relations.RISK_LEVEL.VERY_LOW)
        self.assertTrue(self.hero.quest_money_reward_multiplier() < 1.0)

    def test_push_message(self):
        message = messages.MessageSurrogate(turn_number=TimePrototype.get_current_turn_number(),
                                            timestamp=time.time(),
                                            key=None,
                                            externals=None,
                                            message='abrakadabra')

        self.hero.journal.clear()
        self.hero.diary.clear()

        self.assertEqual(len(self.hero.journal), 0)
        self.assertEqual(len(self.hero.diary), 0)

        self.hero.push_message(message)

        self.assertEqual(len(self.hero.journal), 1)
        self.assertEqual(len(self.hero.diary), 0)

        self.hero.push_message(message, diary=True)

        self.assertEqual(len(self.hero.journal), 2)
        self.assertEqual(len(self.hero.diary), 1)

        self.hero.push_message(message, diary=True, journal=False)

        self.assertEqual(len(self.hero.journal), 2)
        self.assertEqual(len(self.hero.diary), 2)

    def test_add_message__inactive_hero(self):

        self.hero.journal.clear()
        self.hero.diary.clear()

        self.hero.journal.updated = False
        self.hero.diary.updated = False

        self.assertTrue(self.hero.is_active)

        with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_1')):
            self.hero.add_message('hero_common_journal_level_up', diary=True, journal=True)

        self.assertEqual(len(self.hero.journal), 1)
        self.assertEqual(len(self.hero.diary), 1)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_active', False):
            with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_2')):
                self.hero.add_message('hero_common_journal_level_up', diary=True, journal=True)

            self.assertEqual(len(self.hero.journal), 2)
            self.assertEqual(len(self.hero.diary), 2)

            with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_2')):
                self.hero.add_message('hero_common_journal_level_up', diary=False, journal=True)

            self.assertEqual(len(self.hero.journal), 0)
            self.assertEqual(len(self.hero.diary), 2)

            with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_2')):
                with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
                    self.hero.add_message('hero_common_journal_level_up', diary=False, journal=True)

            self.assertEqual(len(self.hero.journal), 1)
            self.assertEqual(len(self.hero.diary), 2)



    def test_energy_maximum(self):
        maximum_without_premium = self.hero.energy_maximum
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        maximum_with_premium = self.hero.energy_maximum
        self.assertTrue(maximum_without_premium < maximum_with_premium)

    def test_energy(self):
        self.hero.energy = 6
        self.hero.add_energy_bonus(100)

        self.assertEqual(self.hero.energy, 6)
        self.assertEqual(self.hero.energy_full, 106 + heroes_settings.START_ENERGY_BONUS)

    def test_change_energy__plus(self):
        self.hero.energy = 6
        self.hero.add_energy_bonus(100)

        self.assertEqual(self.hero.change_energy(self.hero.energy_maximum), self.hero.energy_maximum - 6)
        self.assertEqual(self.hero.energy_bonus, 100 + heroes_settings.START_ENERGY_BONUS)

    def test_change_energy__minus(self):
        self.hero.energy = 6
        self.hero.add_energy_bonus(100 - heroes_settings.START_ENERGY_BONUS)

        self.assertEqual(self.hero.change_energy(-50), -50)
        self.assertEqual(self.hero.energy_bonus, 56)

        self.assertEqual(self.hero.change_energy(-100), -56)
        self.assertEqual(self.hero.energy_bonus, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.energy_discount', 1)
    def test_change_energy__discount(self):
        self.hero.energy = 6
        self.hero.add_energy_bonus(100 - heroes_settings.START_ENERGY_BONUS)

        self.assertEqual(self.hero.change_energy(-50), -49)
        self.assertEqual(self.hero.energy_bonus, 57)

        self.assertEqual(self.hero.change_energy(-100), -57)
        self.assertEqual(self.hero.energy_bonus, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.energy_discount', 100)
    def test_change_energy__discount__no_less_1(self):
        self.hero.energy = 6
        self.hero.add_energy_bonus(-heroes_settings.START_ENERGY_BONUS)

        self.assertEqual(self.hero.change_energy(-50), -1)
        self.assertEqual(self.hero.energy, 5)


    def check_rests_from_risk(self, method):
        results = []
        for risk_level in relations.RISK_LEVEL.records:
            values = []
            self.hero.preferences.set_risk_level(risk_level)
            for health_percents in xrange(1, 100, 1):
                self.hero.health = self.hero.max_health * float(health_percents) / 100
                values.append(method(self.hero))
            results.append(values)

        for i, result_1 in enumerate(results):
            for j, result_2 in enumerate(results):
                if i == j:
                    continue
                self.assertNotEqual(result_1, result_2)

    def test_need_rest_in_settlement__from_risk_level(self):
        self.check_rests_from_risk(lambda hero: hero.need_rest_in_settlement)

    def test_need_rest_in_move__from_risk_level(self):
        self.check_rests_from_risk(lambda hero: hero.need_rest_in_move)

    @mock.patch('the_tale.game.heroes.conf.heroes_settings.RARE_OPERATIONS_INTERVAL', 2)
    def test_process_rare_operations__interval_not_passed(self):
        game_time = TimePrototype.get_current_time()
        game_time.increment_turn()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [])
        self.assertEqual(self.hero.last_rare_operation_at_turn, 0)

    @mock.patch('the_tale.game.heroes.conf.heroes_settings.RARE_OPERATIONS_INTERVAL', 2)
    def test_process_rare_operations__interval_passed(self):
        game_time = TimePrototype.get_current_time()
        game_time.increment_turn()
        game_time.increment_turn()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            with mock.patch('the_tale.game.quests.container.QuestsContainer.sync_interfered_persons') as sync_interfered_persons:
                self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.TIME,
                                                                        old_value=0,
                                                                        new_value=0)])

        self.assertEqual(sync_interfered_persons.call_args_list, [mock.call()])

        self.assertEqual(self.hero.last_rare_operation_at_turn, game_time.turn_number)


    def test_process_rare_operations__companion_added(self):
        game_time = TimePrototype.get_current_time()
        game_time.turn_number += c.TURNS_IN_GAME_YEAR - 1
        game_time.save()

        self.assertTrue(len(list(companions_storage.companions.enabled_companions())) > 1)

        companions_logic.create_random_companion_record('leaved_companions',
                                                        abilities=companions_abilities_container.Container(start=(companions_effects.ABILITIES.TEMPORARY, )),
                                                        state=companions_relations.STATE.ENABLED)

        with self.check_changed(lambda: self.hero.companion):
            self.hero.process_rare_operations()

        self.assertTrue(any(ability.is_TEMPORARY for ability in self.hero.companion.record.abilities.start))

        self.assertTrue(self.hero.companion.record.rarity.is_COMMON)


    @mock.patch('the_tale.game.heroes.conf.heroes_settings.RARE_OPERATIONS_INTERVAL', 0)
    def test_process_rare_operations__companion_not_added(self):

        for i in xrange(1000):
            self.hero.process_rare_operations()
            self.assertEqual(self.hero.companion, None)


    def test_process_rare_operations__age_changed(self):
        game_time = TimePrototype.get_current_time()
        game_time.turn_number += c.TURNS_IN_GAME_YEAR - 1
        game_time.save()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.TIME,
                                                                        old_value=0,
                                                                        new_value=0)])

        self.hero.last_rare_operation_at_turn = 0

        game_time.increment_turn()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.TIME,
                                                                        old_value=0,
                                                                        new_value=1)])


    def test_get_achievement_type_value(self):
        for achievement_type in ACHIEVEMENT_TYPE.records:
            if achievement_type.source.is_ACCOUNT:
                continue
            if achievement_type.source.is_NONE:
                continue
            self.hero.get_achievement_type_value(achievement_type)

    def test_update_habits__premium(self):
        self.assertEqual(self.hero.habit_honor.raw_value, 0)
        self.assertFalse(self.hero.is_premium)

        self.hero.update_habits(relations.HABIT_CHANGE_SOURCE.QUEST_HONORABLE)

        value_without_premium = self.hero.habit_honor.raw_value

        with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
            self.hero.update_habits(relations.HABIT_CHANGE_SOURCE.QUEST_HONORABLE)

        self.assertTrue(value_without_premium < self.hero.habit_honor.raw_value - value_without_premium)


    def test_reset_accessories_cache(self):
        self.hero.damage_modifier # fill cache

        self.assertTrue(getattr(self.hero, '_cached_modifiers'))

        self.hero.reset_accessors_cache()

        self.assertEqual(self.hero._cached_modifiers, {relations.MODIFIERS.HEALTH: 1.0})

    @mock.patch('the_tale.game.balance.power.Power.damage', lambda self: Damage(1, 1))
    @mock.patch('the_tale.game.heroes.objects.Hero.damage_modifier', 2)
    @mock.patch('the_tale.game.heroes.objects.Hero.magic_damage_modifier', 3)
    @mock.patch('the_tale.game.heroes.objects.Hero.physic_damage_modifier', 4)
    def test_basic_damage(self):
        self.assertEqual(self.hero.basic_damage, Damage(physic=8, magic=6))


    def test_set_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)

        self.assertEqual(self.hero.companion, None)

        with self.check_delta(self.hero.diary.__len__, 1):
            self.hero.set_companion(companion)

        self.assertTrue(self.hero.diary.messages[-1].key.is_COMPANIONS_RECEIVED)
        self.assertEqual(self.hero.companion.record.id, companion_record.id)
        self.assertEqual(self.hero.companion._hero.id, self.hero.id)


    @mock.patch('the_tale.game.heroes.objects.Hero.companion_max_health_multiplier', 2)
    def test_set_companion__health_maximum(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        self.assertEqual(self.hero.companion.health, self.hero.companion.max_health)


    def test_set_companion__replace(self):
        companion_record_1 = list(companions_storage.companions.enabled_companions())[0]
        companion_record_2 = list(companions_storage.companions.enabled_companions())[1]

        companion_1 = companions_logic.create_companion(companion_record_1)
        companion_2 = companions_logic.create_companion(companion_record_2)

        self.hero.set_companion(companion_1)

        with self.check_delta(self.hero.diary.__len__, 2):
            self.hero.set_companion(companion_2)

        self.assertTrue(self.hero.diary.messages[-2].key.is_COMPANIONS_LEFT)
        self.assertTrue(self.hero.diary.messages[-1].key.is_COMPANIONS_RECEIVED)

        self.assertEqual(self.hero.companion.record.id, companion_record_2.id)

    def test_remove_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.hero.remove_companion()

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.hero.companion, None)


    def test_remove_companion__switch_next_spending(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        while not self.hero.next_spending.is_HEAL_COMPANION:
            self.hero.switch_spending()

        self.hero.remove_companion()

        self.assertFalse(self.hero.next_spending.is_HEAL_COMPANION)


    def test_switch_next_spending__with_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        spendings = set()

        for i in xrange(1000):
            self.hero.switch_spending()
            spendings.add(self.hero.next_spending)

        self.assertIn(relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION, spendings)

    def test_switch_next_spending__with_companion_dedication_is_EVERY_MAN_FOR_HIMSELF(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        self.hero.preferences.set_companion_dedication(relations.COMPANION_DEDICATION.EVERY_MAN_FOR_HIMSELF)

        for i in xrange(1000):
            self.hero.switch_spending()
            self.assertFalse(self.hero.next_spending.is_HEAL_COMPANION)

    def test_next_spending_priorities_depends_from_dedication(self):
        heal_companion_priorities = set()

        for dedication in relations.COMPANION_DEDICATION.records:
            self.hero.preferences.set_companion_dedication(dedication)
            heal_companion_priorities.add(self.hero.spending_priorities()[relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION])

        self.assertEqual(len(heal_companion_priorities), len(relations.COMPANION_DEDICATION.records))


    def test_switch_next_spending__without_companion(self):
        self.assertEqual(self.hero.companion, None)

        for i in xrange(1000):
            self.hero.switch_spending()
            self.assertFalse(self.hero.next_spending.is_HEAL_COMPANION)

    def test_actual_bills_number(self):
        self.hero.actual_bills.append(time.time() - bills_conf.bills_settings.BILL_ACTUAL_LIVE_TIME*24*60*60)
        self.hero.actual_bills.append(time.time() - bills_conf.bills_settings.BILL_ACTUAL_LIVE_TIME*24*60*60 + 1)
        self.hero.actual_bills.append(time.time() - 1)
        self.hero.actual_bills.append(time.time())

        self.assertEqual(self.hero.actual_bills_number, 3)


class HeroLevelUpTests(testcase.TestCase):

    def setUp(self):
        super(HeroLevelUpTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    def test_is_initial_state(self):
        self.assertTrue(self.hero.abilities.is_initial_state())

        self.hero.randomized_level_up(increment_level=True)

        self.assertFalse(self.hero.abilities.is_initial_state())

        self.hero.abilities.reset()

        self.assertTrue(self.hero.abilities.is_initial_state())

    def test_level_up(self):

        with self.check_delta(MessagePrototype._db_count, 4):
            self.assertEqual(self.hero.level, 1)
            self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

            self.hero.add_experience(f.exp_on_lvl(1)/2 / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 1)

            self.hero.add_experience(f.exp_on_lvl(1) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 2)
            self.assertEqual(self.hero.experience, f.exp_on_lvl(1)/2)

            self.hero.add_experience(f.exp_on_lvl(2) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 3)

            self.hero.add_experience(f.exp_on_lvl(3) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 4)

            self.hero.add_experience(f.exp_on_lvl(4) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 5)

    def test_increment_level__no_message(self):
        with self.check_not_changed(MessagePrototype._db_count):
            self.hero.increment_level()

    def test_increment_level__message(self):
        with self.check_delta(MessagePrototype._db_count, 1):
            self.hero.increment_level(send_message=True)

    def test_increment_level__force_save(self):
        self.assertFalse(self.hero.force_save_required)
        self.hero.increment_level()
        self.assertTrue(self.hero.force_save_required)

    def test_max_ability_points_number(self):
        level_to_points_number = { 1: 3,
                                   2: 4,
                                   3: 5,
                                   4: 6,
                                   5: 7}

        for level, points_number in level_to_points_number.items():
            self.hero.level = level
            self.assertEqual(self.hero.abilities.max_ability_points_number, points_number)


    def test_can_choose_new_ability(self):
        self.assertTrue(self.hero.abilities.can_choose_new_ability)
        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.current_ability_points_number', 3):
            self.assertFalse(self.hero.abilities.can_choose_new_ability)

    def test_next_battle_ability_point_lvl(self):
        level_to_next_level = { 1: 2,
                                2: 5,
                                3: 5,
                                4: 5,
                                5: 8,
                                6: 8,
                                7: 8,
                                8: 11,
                                9: 11,
                                10: 11,
                                11: 14,
                                12: 14,
                                13: 14,
                                14: 17,
                                15: 17}

        for level, next_level in level_to_next_level.items():
            self.hero.reset_level()

            for i in xrange(level-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_battle_ability_point_lvl, next_level)

    def test_next_nonbattle_ability_point_lvl(self):
        level_to_next_level = { 1: 3,
                                2: 3,
                                3: 6,
                                4: 6,
                                5: 6,
                                6: 9,
                                7: 9,
                                8: 9,
                                9: 12,
                                10: 12,
                                11: 12,
                                12: 15,
                                13: 15,
                                14: 15,
                                15: 18,
                                16: 18}

        for level, next_level in level_to_next_level.items():
            self.hero.reset_level()

            for i in xrange(level-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_nonbattle_ability_point_lvl, next_level)


    def test_next_companion_ability_point_lvl(self):
        level_to_next_level = { 1: 4,
                                2: 4,
                                3: 4,
                                4: 7,
                                5: 7,
                                6: 7,
                                7: 10,
                                8: 10,
                                9: 10,
                                10: 13,
                                11: 13,
                                12: 13,
                                13: 16,
                                14: 16}

        for level, next_level in level_to_next_level.items():
            self.hero.reset_level()

            for i in xrange(level-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_companion_ability_point_lvl, next_level)

    def test_next_ability_type(self):
        ability_points_to_type = {1: ABILITY_TYPE.BATTLE,
                                  2: ABILITY_TYPE.NONBATTLE,
                                  3: ABILITY_TYPE.COMPANION,
                                  4: ABILITY_TYPE.BATTLE,
                                  5: ABILITY_TYPE.NONBATTLE,
                                  6: ABILITY_TYPE.COMPANION,

                                  50: ABILITY_TYPE.NONBATTLE,
                                  51: ABILITY_TYPE.COMPANION,
                                  52: ABILITY_TYPE.BATTLE,
                                  53: ABILITY_TYPE.NONBATTLE,
                                  54: ABILITY_TYPE.COMPANION,
                                  55: ABILITY_TYPE.BATTLE,
                                  56: ABILITY_TYPE.NONBATTLE,
                                  57: ABILITY_TYPE.COMPANION,
                                  58: ABILITY_TYPE.BATTLE,
                                  59: ABILITY_TYPE.NONBATTLE,

                                  60: ABILITY_TYPE.BATTLE,
                                  61: ABILITY_TYPE.BATTLE,
                                  62: ABILITY_TYPE.BATTLE,
                                  63: ABILITY_TYPE.BATTLE,
                                  64: ABILITY_TYPE.BATTLE,
                                  65: ABILITY_TYPE.BATTLE,
                                  66: ABILITY_TYPE.BATTLE,
                                  67: ABILITY_TYPE.BATTLE,
                                  68: ABILITY_TYPE.BATTLE,
                                  69: ABILITY_TYPE.BATTLE,
                                  70: None,
                                  71: None,
                                  72: None,
                                  73: None}

        for ability_points, next_type in ability_points_to_type.iteritems():
            self.hero.reset_level()
            for i in xrange(ability_points-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_ability_type, next_type)


    def test_get_abilities_for_choose_first_time(self):
        abilities = self.hero.abilities.get_for_choose()
        self.assertEqual(len(abilities), c.ABILITIES_FOR_CHOOSE_MAXIMUM)

    def test_get_abilities_for_choose_has_free_slots(self):
        for ability in self.hero.abilities.abilities.values():
            ability.level = ability.MAX_LEVEL
        abilities = self.hero.abilities.get_for_choose()
        self.assertEqual(len(abilities), 4)
        self.assertEqual(len(filter(lambda a: a.level==2 and a.get_id()=='hit', abilities)), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_passive_slots_busy(self):

        passive_abilities = filter(lambda a: a.activation_type.is_PASSIVE and a.type.is_BATTLE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len(filter(lambda a: a.activation_type.is_PASSIVE, abilities)), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_active_slots_busy(self):
        active_abilities = filter(lambda a: a.activation_type.is_ACTIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len(filter(lambda a: a.activation_type.is_ACTIVE, abilities)), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy(self):
        passive_abilities = filter(lambda a: a.activation_type.is_PASSIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type.is_ACTIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len(abilities), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy_but_one_not_max_level(self):
        passive_abilities = filter(lambda a: a.activation_type.is_PASSIVE and a.availability.value & ABILITY_AVAILABILITY.FOR_PLAYERS.value,
                                   [a(level=a.MAX_LEVEL) for a in battle.ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type.is_ACTIVE and a.availability.value & ABILITY_AVAILABILITY.FOR_PLAYERS.value,
                                  [a(level=a.MAX_LEVEL) for a in battle.ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        ability = random.choice([ability for ability in self.hero.abilities.abilities.values() if ability.TYPE.is_BATTLE])
        ability.level -= 1

        for i in xrange(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(abilities, [ability.__class__(level=ability.level+1)])

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy_and_all_not_max_level(self):
        passive_abilities = filter(lambda a: a.activation_type.is_PASSIVE, [a(level=1) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type.is_ACTIVE, [a(level=1) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len(abilities), c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM)


class HeroQuestsTest(testcase.TestCase):

    def setUp(self):
        super(HeroQuestsTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = logic.load_hero(account_id=account_id)

        self.place = places_storage.all()[0]
        self.person = self.place.persons[0]


    def test_character_quests__hometown(self):
        self.assertFalse(QUESTS.HOMETOWN in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.preferences.set_place(self.place)
        self.hero.position.set_place(self.place)
        self.assertFalse(QUESTS.HOMETOWN in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(QUESTS.HOMETOWN in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests__friend(self):
        self.assertFalse(QUESTS.HELP_FRIEND in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.preferences.set_friend(self.person)
        self.hero.position.set_place(self.place)
        self.assertFalse(QUESTS.HELP_FRIEND in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(QUESTS.HELP_FRIEND in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests__enemy(self):
        self.assertFalse(QUESTS.INTERFERE_ENEMY in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.preferences.set_enemy(self.person)
        self.hero.position.set_place(self.place)
        self.assertFalse(QUESTS.INTERFERE_ENEMY in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(QUESTS.INTERFERE_ENEMY in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests__hunt(self):
        self.assertFalse(QUESTS.HUNT in [quest for quest, priority in self.hero.get_quests_priorities()])
        self.hero.preferences.set_mob(mobs_storage.all()[0])
        self.assertTrue(QUESTS.HUNT in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests_searchsmith_with_preferences_without_artifact(self):
        self.hero.equipment._remove_all()
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.PLATE)
        logic.save_hero(self.hero)

        self.assertTrue(QUESTS.SEARCH_SMITH in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests_searchsmith_with_preferences_with_artifact(self):
        self.hero.preferences.set_equipment_slot(relations.EQUIPMENT_SLOT.PLATE)
        logic.save_hero(self.hero)

        self.assertTrue(self.hero.equipment.get(relations.EQUIPMENT_SLOT.PLATE) is not None)
        self.assertTrue(QUESTS.SEARCH_SMITH in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_unique_quests__pilgrimage(self):
        self.assertFalse(QUESTS.PILGRIMAGE in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.place.modifier = CITY_MODIFIERS.HOLY_CITY
        self.hero.position.set_place(self.place)
        self.assertFalse(QUESTS.PILGRIMAGE in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(QUESTS.PILGRIMAGE in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_get_minimum_created_time_of_active_quests(self):
        with mock.patch('the_tale.game.quests.container.QuestsContainer.min_quest_created_time', datetime.datetime.now() - datetime.timedelta(days=1)):
            logic.save_hero(self.hero)

        account = self.accounts_factory.create_account()
        hero = logic.load_hero(account_id=account.id)

        test_time = datetime.datetime.now() - datetime.timedelta(days=2)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.min_quest_created_time', test_time):
            logic.save_hero(hero)

        # not there are no another quests an get_minimum_created_time_of_active_quests return now()
        self.assertEqual(test_time, logic.get_minimum_created_time_of_active_quests())


    def test_modify_quest_priority(self):
        self.assertEqual(self.hero.modify_quest_priority(QUESTS.HELP_FRIEND), QUESTS.HELP_FRIEND.priority)
        self.assertEqual(self.hero.modify_quest_priority(QUESTS.INTERFERE_ENEMY), QUESTS.INTERFERE_ENEMY.priority)

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_3)
    def test_modify_quest_priority__friend(self):
        self.assertTrue(self.hero.modify_quest_priority(QUESTS.HELP_FRIEND) > QUESTS.HELP_FRIEND.priority)
        self.assertEqual(self.hero.modify_quest_priority(QUESTS.INTERFERE_ENEMY), QUESTS.INTERFERE_ENEMY.priority)

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_3)
    def test_modify_quest_priority__enemy(self):
        self.assertEqual(self.hero.modify_quest_priority(QUESTS.HELP_FRIEND), QUESTS.HELP_FRIEND.priority)
        self.assertTrue(self.hero.modify_quest_priority(QUESTS.INTERFERE_ENEMY)> QUESTS.INTERFERE_ENEMY.priority)



class HeroUiInfoTest(testcase.TestCase):

    def setUp(self):
        super(HeroUiInfoTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    def test_is_ui_caching_required(self):
        self.assertTrue(self.hero.is_ui_caching_required) # new hero must be cached, since player, who created him, is in game
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME + 1)
        self.assertFalse(self.hero.is_ui_caching_required)


    ########################
    # recache required
    ########################

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_from_cache__from_cache_is_true__for_not_visited_heroes(self):
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME + 1)
        logic.save_hero(self.hero)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none__game_stopped(self):
        GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))


    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_exists(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_not_exists(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_exists(self):
        GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_not_exists(self):
        GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', lambda x: get_simple_cache_data(ui_caching_started_at=time.time()))
    def test_cached_ui_info_for_hero__continue_caching_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)


    ########################
    # recache not required
    ########################
    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_from_cache__from_cache_is_true__for_not_visited_heroes__recache_not_required(self):
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME + 1)
        logic.save_hero(self.hero)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none__game_stopped__recache_not_required(self):
        GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))


    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_exists__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_not_exists__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_exists__recache_not_required(self):
        GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_not_exists__recache_not_required(self):
        GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', lambda x: get_simple_cache_data(ui_caching_started_at=time.time()))
    def test_cached_ui_info_for_hero__continue_caching_not_required__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)


    @mock.patch('dext.common.utils.cache.get', lambda x: {'ui_caching_started_at': time.time(),
                                                          'a': 1,
                                                          'b': 2,
                                                          'c': 3,
                                                          'd': 4,
                                                          'pvp__actual': 'x',
                                                          'pvp__last_turn': 'y',
                                                          'patch_turn': 666,
                                                          'changed_fields': ['b', 'c', 'changed_fields', 'patch_turn']})
    def test_cached_ui_info_for_hero__make_patch(self):
        data = objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=[666], for_last_turn=False)
        self.assertEqual(data,
                         {'b': 2,
                          'c': 3,
                          'patch_turn': 666})

    def test_cached_ui_info_for_hero__turn_in_patch_turns(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        old_info['patch_turn'] = 666
        old_info['changed_fields'].extend(field for field in old_info.iterkeys()
                                          if random.random() < 0.5 and field not in ('pvp__last_turn', 'pvp__actual'))

        with mock.patch('dext.common.utils.cache.get', lambda x: copy.deepcopy(old_info)):
            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=[665, 666, 667], for_last_turn=False)

        self.assertNotEqual(data['patch_turn'], None)
        self.assertEqual(set(data.keys()) | set(('changed_fields',)), set(old_info['changed_fields']))


    def test_cached_ui_info_for_hero__turn_not_in_patch_turns(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        old_info['patch_turn'] = 664
        old_info['changed_fields'].extend(field for field in old_info.iterkeys()
                                          if random.random() < 0.5 and field not in ('pvp__last_turn', 'pvp__actual'))

        with mock.patch('dext.common.utils.cache.get', lambda x: copy.deepcopy(old_info)):
            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=[665, 666, 667], for_last_turn=False)

        self.assertEqual(set(data.keys()) | set(('changed_fields', 'pvp__last_turn', 'pvp__actual')),
                         set(self.hero.ui_info(actual_guaranteed=True, old_info=None).keys()) | set(('pvp',)))
        self.assertEqual(data['patch_turn'], None)

    def test_cached_ui_info_for_hero__actual_info(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        old_info['pvp__last_turn'] = 'last_turn'
        old_info['pvp__actual'] = 'actual'

        with mock.patch('dext.common.utils.cache.get', lambda x: copy.deepcopy(old_info)):
            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
            self.assertEqual(data['pvp'], 'actual')
            self.assertNotIn('pvp__last_turn', data)
            self.assertNotIn('pvp__actual', data)

            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=True)
            self.assertEqual(data['pvp'], 'last_turn')
            self.assertNotIn('pvp__last_turn', data)
            self.assertNotIn('pvp__actual', data)


    def test_ui_info_patch(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)

        patched_fields = set(field for field in old_info.iterkeys() if random.random() < 0.5)
        patched_fields |= set(('changed_fields', 'actual_on_turn', 'patch_turn'))

        for field in patched_fields:
            old_info[field] = 'changed'

        new_info = self.hero.ui_info(actual_guaranteed=True, old_info=old_info)

        self.assertEqual(new_info['patch_turn'], old_info['actual_on_turn'])
        self.assertEqual(set(new_info['changed_fields']), patched_fields)

    def test_ui_info__always_changed_fields(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        new_info = self.hero.ui_info(actual_guaranteed=True, old_info=old_info)

        self.assertEqual(set(new_info['changed_fields']), set(('changed_fields', 'actual_on_turn', 'patch_turn')))

    def test_ui_info__actual_guaranteed(self):
        self.assertEqual(self.hero.saved_at_turn, 0)

        self.assertEqual(self.hero.ui_info(actual_guaranteed=True)['actual_on_turn'], 0)
        self.assertEqual(self.hero.ui_info(actual_guaranteed=False)['actual_on_turn'], 0)

        TimePrototype(turn_number=666).save()

        self.assertEqual(self.hero.ui_info(actual_guaranteed=True)['actual_on_turn'], 666)
        self.assertEqual(self.hero.ui_info(actual_guaranteed=False)['actual_on_turn'], 0)

        logic.save_hero(self.hero)

        self.assertTrue(self.hero.saved_at_turn, 666)

        self.assertEqual(self.hero.ui_info(actual_guaranteed=True)['actual_on_turn'], 666)
        self.assertEqual(self.hero.ui_info(actual_guaranteed=False)['actual_on_turn'], 666)

    def test_ui_caching_timeout_greate_then_turn_delta(self):
        self.assertTrue(heroes_settings.UI_CACHING_TIMEOUT > c.TURN_DELTA)

    def test_is_ui_continue_caching_required(self):
        self.assertTrue(objects.Hero.is_ui_continue_caching_required(0))
        self.assertFalse(objects.Hero.is_ui_continue_caching_required(time.time() - (heroes_settings.UI_CACHING_TIME - heroes_settings.UI_CACHING_CONTINUE_TIME - 1)))
        self.assertTrue(objects.Hero.is_ui_continue_caching_required(time.time() - (heroes_settings.UI_CACHING_TIME - heroes_settings.UI_CACHING_CONTINUE_TIME + 1)))
        self.assertTrue(objects.Hero.is_ui_continue_caching_required(time.time() - heroes_settings.UI_CACHING_TIME))
