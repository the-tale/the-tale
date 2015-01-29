# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions import logic
from the_tale.game.companions import objects
from the_tale.game.companions import relations



class CompanionTests(testcase.TestCase):

    def setUp(self):
        super(CompanionTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.companion_record = logic.create_companion_record(utg_name=names.generator.get_test_name(),
                                                              description='description',
                                                              type=relations.TYPE.random(),
                                                              max_health=10,
                                                              dedication=relations.DEDICATION.random(),
                                                              rarity=relations.RARITY.random(),
                                                              archetype=game_relations.ARCHETYPE.random(),
                                                              state=relations.STATE.ENABLED)

        self.companion = logic.create_companion(self.companion_record)

    def test_initialization(self):
        self.assertEqual(self.companion.health, 10)
        self.assertEqual(self.companion.experience, 0)
        self.assertEqual(self.companion.coherence, c.COMPANIONS_MIN_COHERENCE)

    def test_serialization(self):
        self.assertEqual(self.companion.serialize(),
                         objects.Companion.deserialize(None, self.companion.serialize()).serialize())

    def test_experience_to_next_level(self):
        self.assertEqual(self.companion.experience_to_next_level, f.companions_coherence_for_level(1))

        self.companion.coherence = 5
        self.assertEqual(self.companion.experience_to_next_level, f.companions_coherence_for_level(6))

    def test_experience_to_next_level__max_level(self):
        self.companion.coherence = c.COMPANIONS_MAX_COHERENCE-1

        with self.check_not_changed(lambda: self.companion.experience_to_next_level):
            self.companion.coherence = c.COMPANIONS_MAX_COHERENCE

    def test_add_experience__level_not_changed(self):
        self.companion.coherence = 5

        with self.check_not_changed(lambda: self.companion.coherence):
            self.companion.add_experience(1)

        self.assertEqual(self.companion.experience, 1)

    def test_add_experience__level_changed(self):
        self.companion.coherence = 5

        with self.check_delta(lambda: self.companion.coherence, 1):
            self.companion.add_experience(self.companion.experience_to_next_level+2)

        self.assertEqual(self.companion.experience, 2)

    def test_add_experience__2_levels_changed(self):
        self.companion.coherence = 5

        with self.check_delta(lambda: self.companion.coherence, 2):
            self.companion.add_experience(self.companion.experience_to_next_level+f.companions_coherence_for_level(7)+2)

        self.assertEqual(self.companion.experience, 2)

    def test_add_experience__max_level(self):
        self.companion.coherence = c.COMPANIONS_MAX_COHERENCE

        with self.check_not_changed(lambda: self.companion.coherence):
            self.companion.add_experience(66666666666)

        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

    @mock.patch('the_tale.game.balance.formulas.companions_heal_in_hour', mock.Mock(return_value=1))
    def test_need_heal_in_move(self):
        self.companion.healed_at -= 60*60
        self.companion.health = self.companion.max_health

        self.assertFalse(self.companion.need_heal_in_move)

        self.companion.health -= 1

        self.assertTrue(self.companion.need_heal_in_move)


    @mock.patch('the_tale.game.balance.formulas.companions_heal_in_hour', mock.Mock(return_value=1))
    def test_need_heal_in_move__no_time(self):
        self.companion.healed_at -= 30*60
        self.companion.health = self.companion.max_health

        self.assertFalse(self.companion.need_heal_in_move)

        self.companion.health -= 1

        self.assertFalse(self.companion.need_heal_in_move)


    @mock.patch('the_tale.game.balance.formulas.companions_heal_in_hour', mock.Mock(return_value=1))
    def test_need_heal_in_settlement(self):
        self.companion.healed_at -= 60*60
        self.companion.health = self.companion.max_health

        self.assertFalse(self.companion.need_heal_in_settlement)

        self.companion.health -= 1

        self.assertTrue(self.companion.need_heal_in_settlement)


    @mock.patch('the_tale.game.balance.formulas.companions_heal_in_hour', mock.Mock(return_value=1))
    def test_need_heal_in_settlement__no_time(self):
        self.companion.healed_at -= 30*60
        self.companion.health = self.companion.max_health

        self.assertFalse(self.companion.need_heal_in_settlement)

        self.companion.health -= 1

        self.assertFalse(self.companion.need_heal_in_settlement)


    def test_defend_in_battle_probability__hero_dedication(self):
        self.hero.set_companion(self.companion)

        with self.check_increased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.EGOISM)

        with self.check_decreased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.NORMAL)

        with self.check_decreased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.ALTRUISM)


    def test_defend_in_battle_probability__companion_dedication(self):
        self.companion_record.dedication = relations.DEDICATION.records[0]
        self.hero.set_companion(self.companion)

        for dedication in relations.DEDICATION.records[1:]:
            with self.check_increased(lambda: self.hero.companion.defend_in_battle_probability):
                self.companion_record.dedication = dedication


    def test_defend_in_battle_probability__coherence(self):
        self.hero.set_companion(self.companion)

        with self.check_increased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.companion.coherence = 100
