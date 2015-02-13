# coding: utf-8
import random
import mock

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations as heroes_relations
from the_tale.game.heroes.habilities import companions as heroes_companions_abilities

from the_tale.game.companions import logic
from the_tale.game.companions import objects
from the_tale.game.companions import relations

from the_tale.game.companions.abilities import container as abilities_container
from the_tale.game.companions.abilities import effects as companions_effects


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
                                                              archetype=game_relations.ARCHETYPE.random(),
                                                              mode=relations.MODE.random(),
                                                              abilities=abilities_container.Container(),
                                                              state=relations.STATE.ENABLED)
        self.hero.set_companion(logic.create_companion(self.companion_record))
        self.companion = self.hero.companion

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


    def test_add_experience__coherence_speed__living(self):
        self.companion.coherence = 95

        self.companion.record.type = relations.TYPE.LIVING

        with self.check_delta(lambda: self.companion.experience, 10):
            self.companion.add_experience(10)

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_living_coherence_speed', 2):
            with self.check_delta(lambda: self.companion.experience, 20):
                self.companion.add_experience(10)

            self.companion.record.type = relations.TYPE.random(exclude=(relations.TYPE.LIVING, ))

            with self.check_delta(lambda: self.companion.experience, 10):
                self.companion.add_experience(10)

    def test_add_experience__coherence_speed__construct(self):
        self.companion.coherence = 95

        self.companion.record.type = relations.TYPE.CONSTRUCT

        with self.check_delta(lambda: self.companion.experience, 10):
            self.companion.add_experience(10)

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_construct_coherence_speed', 2):
            with self.check_delta(lambda: self.companion.experience, 20):
                self.companion.add_experience(10)

            self.companion.record.type = relations.TYPE.random(exclude=(relations.TYPE.CONSTRUCT, ))

            with self.check_delta(lambda: self.companion.experience, 10):
                self.companion.add_experience(10)


    def test_add_experience__coherence_speed__unusual(self):
        self.companion.coherence = 95

        self.companion.record.type = relations.TYPE.UNUSUAL

        with self.check_delta(lambda: self.companion.experience, 10):
            self.companion.add_experience(10)

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_unusual_coherence_speed', 2):
            with self.check_delta(lambda: self.companion.experience, 20):
                self.companion.add_experience(10)

            self.companion.record.type = relations.TYPE.random(exclude=(relations.TYPE.UNUSUAL, ))

            with self.check_delta(lambda: self.companion.experience, 10):
                self.companion.add_experience(10)


    def test_add_experience__level_not_changed(self):
        self.companion.coherence = 5

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.reset_accessors_cache') as reset_accessors_cache:
            with self.check_not_changed(lambda: self.companion.coherence):
                self.companion.add_experience(1)

        self.assertEqual(reset_accessors_cache.call_count, 0)

        self.assertEqual(self.companion.experience, 1)

    def test_add_experience__level_changed(self):
        self.companion.coherence = 5

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.reset_accessors_cache') as reset_accessors_cache:
            with self.check_delta(lambda: self.companion.coherence, 1):
                self.companion.add_experience(self.companion.experience_to_next_level+2)

        self.assertEqual(reset_accessors_cache.call_count, 1)

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

    def test_max_health(self):

        max_health = self.companion.max_health

        with self.check_delta(lambda: max_health, max_health * 0.5):
            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_max_health_multiplier', 1.5):
                max_health = self.companion.max_health


    def test_max_coherence(self):

        max_coherence = self.companion.max_coherence

        with self.check_delta(lambda: max_coherence, 40):
            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_max_coherence', 60):
                max_coherence = self.companion.max_coherence

    def test_coherence_greater_then_maximum(self):

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_max_coherence', 60):
            self.companion.add_experience(6666666)
            self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

        self.assertEqual(self.companion.max_coherence, 20)
        self.assertEqual(self.companion.coherence, 60)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

        self.companion.add_experience(6666666666666)

        self.assertEqual(self.companion.max_coherence, 20)
        self.assertEqual(self.companion.coherence, 60)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

    def test_modify_attribute(self):
        checked_abilities = [ability
                             for ability in heroes_companions_abilities.ABILITIES.itervalues()
                             if issubclass(ability, heroes_companions_abilities._CompanionAbilityModifier)]

        for ability_class in checked_abilities:
            for companion_ability in companions_effects.ABILITIES.records:
                if ability_class.EFFECT_TYPE != companion_ability.effect.TYPE.metatype:
                    continue

                if hasattr(companion_ability.effect, 'ABILITY'): # skip battle abilities
                    continue

                if companion_ability.effect.MODIFIER is None: # skip complex abilities
                    continue

                self.hero.abilities.reset()
                self.hero.reset_accessors_cache()

                self.companion_record.abilities = abilities_container.Container(start=(companion_ability,))

                with self.check_changed(lambda: self.companion.modify_attribute(companion_ability.effect.MODIFIER, companion_ability.effect.MODIFIER.default())):
                    self.hero.abilities.add(ability_class.get_id(), random.randint(1, ability_class.MAX_LEVEL))


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
