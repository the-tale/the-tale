# coding: utf-8
import random

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions import logic
from the_tale.game.companions import relations

from the_tale.game.companions.abilities import effects
from the_tale.game.companions.abilities import container as abilities_container

from the_tale.game.heroes.relations import MODIFIERS


class BaseEffectsTests(testcase.TestCase):

    def setUp(self):
        super(BaseEffectsTests, self).setUp()

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

    def apply_ability(self, ability):
        container = abilities_container.Container(common=(),
                                                  start=frozenset((ability,)),
                                                  coherence=None,
                                                  honor=None,
                                                  peacefulness=None)
        self.companion_record.abilities = container
        self.hero.reset_accessors_cache()

    def get_ability(self, *argv):
        return random.choice([ability
                              for ability in effects.ABILITIES.records
                              if any(isinstance(ability.effect, effect) for effect in argv)])


class CommonTests(BaseEffectsTests):

    def test_aprox(self):
        self.assertEqual(effects.aprox(1, 2, 1), 1.2)
        self.assertEqual(effects.aprox(1, 2, 2), 1.4)
        self.assertEqual(effects.aprox(1, 2, 3), 1.6)
        self.assertEqual(effects.aprox(1, 2, 4), 1.8)
        self.assertEqual(effects.aprox(1, 2, 5), 2)


class CoherenceSpeedTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CoherenceSpeed(0.8)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COHERENCE_EXPERIENCE, 10), 8)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COHERENCE_EXPERIENCE, 11), 8.8)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COHERENCE_EXPERIENCE,)), 11), 11)

        effect = effects.CoherenceSpeed(1.2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COHERENCE_EXPERIENCE, 10), 12)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COHERENCE_EXPERIENCE, 11), 13.2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COHERENCE_EXPERIENCE,)), 11), 11)


    def test_in_game(self):
        ability = self.get_ability(effects.CoherenceSpeed)

        self.hero.companion.coherence = c.COMPANIONS_MAX_COHERENCE - 1
        self.hero.companion.experience = 0

        self.hero.companion.add_experience(10)

        old_delta = self.hero.companion.experience
        self.hero.companion.experience = 0

        self.apply_ability(ability)

        self.hero.companion.add_experience(10)

        new_delta = self.hero.companion.experience

        self.assertEqual(int(round(old_delta * ability.effect.multiplier_left)), new_delta)


class ChangeHabitsTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR,
                                      habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                     heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2))
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.HABITS_SOURCES, set()), set((heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                                                         heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2)))
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.HABITS_SOURCES,)), set()), set())


    def check_habits_changed(self, honor, peacefulness, honor_check, peacefulness_check):
        self.hero.habit_honor.set_habit(honor)
        self.hero.habit_peacefulness.set_habit(peacefulness)

        for habit_source in self.hero.companion.modify_attribute(heroes_relations.MODIFIERS.HABITS_SOURCES, set()):
            self.hero.update_habits(habit_source)

        self.assertTrue(honor_check(self.hero.habit_honor.raw_value))
        self.assertTrue(peacefulness_check(self.hero.habit_peacefulness.raw_value))


    def test_in_game__aggressive(self):
        self.apply_ability(effects.ABILITIES.AGGRESSIVE)

        self.check_habits_changed(honor=-c.HABITS_BORDER, peacefulness=0,
                                  honor_check=lambda v: v == -c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v < 0)
        self.check_habits_changed(honor=0, peacefulness=c.HABITS_BORDER,
                                  honor_check=lambda v: v == 0,
                                  peacefulness_check=lambda v: v < c.HABITS_BORDER)
        self.check_habits_changed(honor=c.HABITS_BORDER, peacefulness=-c.HABITS_BORDER,
                                  honor_check=lambda v: v == c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == -c.HABITS_BORDER)

    def test_in_game__peaceful(self):
        self.apply_ability(effects.ABILITIES.PEACEFUL)

        self.check_habits_changed(honor=-c.HABITS_BORDER, peacefulness=0,
                                  honor_check=lambda v: v == -c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v > 0)
        self.check_habits_changed(honor=0, peacefulness=c.HABITS_BORDER,
                                  honor_check=lambda v: v == 0,
                                  peacefulness_check=lambda v: v == c.HABITS_BORDER)
        self.check_habits_changed(honor=c.HABITS_BORDER, peacefulness=-c.HABITS_BORDER,
                                  honor_check=lambda v: v == c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v > -c.HABITS_BORDER)

    def test_in_game__reserved(self):
        self.apply_ability(effects.ABILITIES.RESERVED)

        self.check_habits_changed(honor=-c.HABITS_BORDER, peacefulness=0,
                                  honor_check=lambda v: v == -c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == 0)
        self.check_habits_changed(honor=0, peacefulness=c.HABITS_BORDER,
                                  honor_check=lambda v: v == 0,
                                  peacefulness_check=lambda v: v < c.HABITS_BORDER)
        self.check_habits_changed(honor=c.HABITS_BORDER, peacefulness=-c.HABITS_BORDER,
                                  honor_check=lambda v: v == c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v > -c.HABITS_BORDER)

    def test_in_game__canny(self):
        self.apply_ability(effects.ABILITIES.CANNY)

        self.check_habits_changed(honor=-c.HABITS_BORDER, peacefulness=0,
                                  honor_check=lambda v: v > -c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == 0)
        self.check_habits_changed(honor=0, peacefulness=c.HABITS_BORDER,
                                  honor_check=lambda v: v == 0,
                                  peacefulness_check=lambda v: v == c.HABITS_BORDER)
        self.check_habits_changed(honor=c.HABITS_BORDER, peacefulness=-c.HABITS_BORDER,
                                  honor_check=lambda v: v < c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == -c.HABITS_BORDER)

    def test_in_game__honest(self):
        self.apply_ability(effects.ABILITIES.HONEST)

        self.check_habits_changed(honor=-c.HABITS_BORDER, peacefulness=0,
                                  honor_check=lambda v: v > -c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == 0)
        self.check_habits_changed(honor=0, peacefulness=c.HABITS_BORDER,
                                  honor_check=lambda v: v > 0,
                                  peacefulness_check=lambda v: v == c.HABITS_BORDER)
        self.check_habits_changed(honor=c.HABITS_BORDER, peacefulness=-c.HABITS_BORDER,
                                  honor_check=lambda v: v == c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == -c.HABITS_BORDER)

    def test_in_game__sneaky(self):
        self.apply_ability(effects.ABILITIES.SNEAKY)

        self.check_habits_changed(honor=-c.HABITS_BORDER, peacefulness=0,
                                  honor_check=lambda v: v == -c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == 0)
        self.check_habits_changed(honor=0, peacefulness=c.HABITS_BORDER,
                                  honor_check=lambda v: v < 0,
                                  peacefulness_check=lambda v: v == c.HABITS_BORDER)
        self.check_habits_changed(honor=c.HABITS_BORDER, peacefulness=-c.HABITS_BORDER,
                                  honor_check=lambda v: v < c.HABITS_BORDER,
                                  peacefulness_check=lambda v: v == -c.HABITS_BORDER)


class QuestMoneyRewardTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.QuestMoneyReward(0.5)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.QUEST_MONEY_REWARD, 10), 5)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.QUEST_MONEY_REWARD, 11), 5.5)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.QUEST_MONEY_REWARD,)), 11), 11)

        effect = effects.QuestMoneyReward(2.0)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.QUEST_MONEY_REWARD, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.QUEST_MONEY_REWARD, 11), 22)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.QUEST_MONEY_REWARD,)), 11), 11)


    def test_in_game(self):
        ability = self.get_ability(effects.QuestMoneyReward)

        with self.check_changed(lambda: self.hero.quest_money_reward_multiplier()):
            self.apply_ability(ability)


class MaxBagSizeTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.MaxBagSize(666)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.MAX_BAG_SIZE, 10), 676)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.MAX_BAG_SIZE, 11), 677)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.MAX_BAG_SIZE,)), 11), 11)


    def test_in_game(self):
        ability = self.get_ability(effects.MaxBagSize)

        with self.check_changed(lambda: self.hero.max_bag_size):
            self.apply_ability(ability)


class PoliticsPowerTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.PoliticsPower(3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.POWER, 11), 33)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.POWER, )), 11), 11)


    def test_in_game(self):
        ability = self.get_ability(effects.PoliticsPower)

        with self.check_changed(lambda: self.hero.person_power_modifier):
            self.apply_ability(ability)


class MagicDamageBonusTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.MagicDamageBonus(2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.MAGIC_DAMAGE, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.PHYSIC_DAMAGE, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.MAGIC_DAMAGE,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.MagicDamageBonus)

        with self.check_changed(lambda: self.hero.magic_damage_modifier):
            self.apply_ability(ability)


class PhysicDamageBonusTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.PhysicDamageBonus(2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.MAGIC_DAMAGE, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.PHYSIC_DAMAGE, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.PHYSIC_DAMAGE,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.PhysicDamageBonus)

        with self.check_changed(lambda: self.hero.physic_damage_modifier):
            self.apply_ability(ability)


class SpeedTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.Speed(2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.SPEED, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.SPEED,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.Speed)

        with self.check_changed(lambda: self.hero.move_speed):
            self.apply_ability(ability)


class BattleAbilityTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.BattleAbilityFireball()
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.INITIATIVE, 10), 10.25)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.ADDITIONAL_ABILITIES, []), [effect.ability])
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.INITIATIVE, MODIFIERS.ADDITIONAL_ABILITIES)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.BattleAbilityHit,
                                   effects.BattleAbilityStrongHit,
                                   effects.BattleAbilityRunUpPush,
                                   effects.BattleAbilityPoisonCloud,
                                   effects.BattleAbilityFreezing)

        with self.check_changed(lambda: self.hero.initiative):
            with self.check_changed(lambda: len(self.hero.companion.modify_attribute(heroes_relations.MODIFIERS.ADDITIONAL_ABILITIES,
                                                                                     heroes_relations.MODIFIERS.ADDITIONAL_ABILITIES.default()))):
                self.apply_ability(ability)


class InitiativeTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.Initiative(2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.INITIATIVE, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.INITIATIVE,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.Initiative)

        with self.check_changed(lambda: self.hero.initiative):
            self.apply_ability(ability)



class BattleProbabilityTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.BattleProbability(1.5)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.BATTLES_PER_TURN, 10), 11.5)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.BATTLES_PER_TURN,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.BattleProbability)

        with self.check_changed(lambda: self.hero.battles_per_turn_summand):
            self.apply_ability(ability)


class LootProbabilityTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.LootProbability(2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.LOOT_PROBABILITY, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.LOOT_PROBABILITY,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.LootProbability)

        with self.check_changed(lambda: self.hero.loot_probability(mobs_storage.all()[0])):
            self.apply_ability(ability)



class CompanionDamageTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionDamage(3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_DAMAGE, 10), 13)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_DAMAGE,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionDamage)

        with self.check_changed(lambda: self.hero.companion_damage):
            self.apply_ability(ability)


class CompanionDamageProbabilityTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionDamageProbability(3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_DAMAGE_PROBABILITY, 10), 30)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_DAMAGE_PROBABILITY,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionDamageProbability)

        with self.check_changed(lambda: self.hero.companion_damage_probability):
            self.apply_ability(ability)


class CompanionStealMoneyTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionStealMoney(3)
        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_STEAL_MONEY))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_STEAL_MONEY_MULTIPLIER))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_STEAL_MONEY, MODIFIERS.COMPANION_STEAL_MONEY_MULTIPLIER))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_STEAL_MONEY, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_STEAL_MONEY_MULTIPLIER, 10), 30)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_STEAL_MONEY, MODIFIERS.COMPANION_STEAL_MONEY_MULTIPLIER)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionStealMoney)

        with self.check_changed(lambda: self.hero.can_companion_steal_money()):
            with self.check_changed(lambda: self.hero.companion_steal_money_modifier):
                self.apply_ability(ability)


class CompanionStealItemTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionStealItem(3)
        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_STEAL_ITEM))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_STEAL_ITEM_MULTIPLIER))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_STEAL_ITEM, MODIFIERS.COMPANION_STEAL_ITEM))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_STEAL_ITEM, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_STEAL_ITEM_MULTIPLIER, 10), 30)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_STEAL_ITEM, MODIFIERS.COMPANION_STEAL_ITEM_MULTIPLIER)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionStealItem)

        with self.check_changed(lambda: self.hero.can_companion_steal_item()):
            with self.check_changed(lambda: self.hero.companion_steal_artifact_probability_multiplier):
                self.apply_ability(ability)


class CompanionSparePartsTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionSpareParts()
        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_SPARE_PARTS))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_SPARE_PARTS,))))

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionSpareParts)

        with self.check_changed(lambda: self.hero.can_companion_broke_to_spare_parts()):
            self.apply_ability(ability)


class CompanionSayWisdomTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionSayWisdom(3)

        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_SAY_WISDOM))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_SAY_WISDOM_PROBABILITY))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_SAY_WISDOM, MODIFIERS.COMPANION_SAY_WISDOM_PROBABILITY))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_SAY_WISDOM, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_SAY_WISDOM_PROBABILITY, 10), 30)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_SAY_WISDOM, MODIFIERS.COMPANION_SAY_WISDOM_PROBABILITY)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionSayWisdom)

        with self.check_changed(lambda: self.hero.can_companion_say_wisdom()):
            with self.check_changed(lambda: self.hero.companion_say_wisdom_probability):
                self.apply_ability(ability)


class CompanionExpPerHealTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionExpPerHeal(2)
        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_EXP_PER_HEAL))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_EXP_PER_HEAL_PROBABILITY))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_EXP_PER_HEAL, MODIFIERS.COMPANION_EXP_PER_HEAL_PROBABILITY))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_EXP_PER_HEAL, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_EXP_PER_HEAL_PROBABILITY, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_EXP_PER_HEAL, MODIFIERS.COMPANION_EXP_PER_HEAL)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionExpPerHeal)

        with self.check_changed(lambda: self.hero.can_companion_exp_per_heal()):
            with self.check_changed(lambda: self.hero.companion_exp_per_heal_probability):
                self.apply_ability(ability)


class DoubleEnergyRegenerationTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.DoubleEnergyRegeneration(0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.DOUBLE_ENERGY_REGENERATION, 0), 0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.DOUBLE_ENERGY_REGENERATION,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.DoubleEnergyRegeneration)

        with self.check_changed(lambda: self.hero.regenerate_double_energy_probability):
            self.apply_ability(ability)


class CompanionEatCorpsesTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionEatCorpses(3)
        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_EAT_CORPSES))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_EAT_CORPSES_PROBABILITY))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_EAT_CORPSES,MODIFIERS.COMPANION_EAT_CORPSES_PROBABILITY))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_EAT_CORPSES, 1), 1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_EAT_CORPSES_PROBABILITY, 1), 3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_EAT_CORPSES, MODIFIERS.COMPANION_EAT_CORPSES_PROBABILITY)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionEatCorpses)

        with self.check_changed(lambda: self.hero.can_companion_eat_corpses()):
            with self.check_changed(lambda: self.hero.companion_eat_corpses_probability):
                self.apply_ability(ability)


class CompanionRegenerateTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionRegenerate(2)

        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_REGENERATE))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_REGENERATE_PROBABILITY))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_REGENERATE, MODIFIERS.COMPANION_REGENERATE_PROBABILITY))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_REGENERATE, 10), 10)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_REGENERATE_PROBABILITY, 10), 20)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_REGENERATE, MODIFIERS.COMPANION_REGENERATE_PROBABILITY)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionRegenerate)

        with self.check_changed(lambda: self.hero.can_companion_regenerate()):
            with self.check_changed(lambda: self.hero.companion_regenerate_probability):
                self.apply_ability(ability)


class CompanionEatAndDiscountTest(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionEat(0.5)

        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_MONEY_FOR_FOOD))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_MONEY_FOR_FOOD,))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_MONEY_FOR_FOOD, 2), 1.0)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_MONEY_FOR_FOOD,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionEat)

        with self.check_changed(lambda: self.hero.can_companion_eat()):
            with self.check_changed(lambda: self.hero.companion_money_for_food_multiplier):
                self.apply_ability(ability)


class CompanionDrinkArtifactTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionDrinkArtifact(0.5)
        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_DRINK_ARTIFACT))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_DRINK_ARTIFACT_PROBABILITY))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_DRINK_ARTIFACT,MODIFIERS.COMPANION_DRINK_ARTIFACT_PROBABILITY))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_DRINK_ARTIFACT, 2), 2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_DRINK_ARTIFACT_PROBABILITY, 2), 1.0)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_DRINK_ARTIFACT, MODIFIERS.COMPANION_DRINK_ARTIFACT_PROBABILITY,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionDrinkArtifact)

        with self.check_changed(lambda: self.hero.can_companion_drink_artifact()):
            with self.check_changed(lambda: self.hero.companion_drink_artifact_probability):
                self.apply_ability(ability)



class CompanionExorcistTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionExorcist(0.5)

        self.assertTrue(effect._check_attribute(MODIFIERS.COMPANION_EXORCIST))
        self.assertFalse(effect._check_attribute(MODIFIERS.COMPANION_EXORCIST_PROBABILITY))
        self.assertFalse(effect._check_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_EXORCIST, MODIFIERS.COMPANION_EXORCIST_PROBABILITY))))

        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_EXORCIST, 2), 2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_EXORCIST_PROBABILITY, 2), 1.0)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_EXORCIST, MODIFIERS.COMPANION_EXORCIST_PROBABILITY,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionExorcist)

        with self.check_changed(lambda: self.hero.can_companion_do_exorcism()):
            with self.check_changed(lambda: self.hero.companion_do_exorcism_probability):
                self.apply_ability(ability)


class RestLenghtTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.RestLenght(3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.REST_LENGTH, 12), 36)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.REST_LENGTH,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.RestLenght)

        with self.check_changed(lambda: self.hero.rest_length):
            self.apply_ability(ability)



class IDLELenghtTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.IDLELenght(3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.IDLE_LENGTH, 12), 36)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.IDLE_LENGTH,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.IDLELenght)

        with self.check_changed(lambda: self.hero.idle_length):
            self.apply_ability(ability)


class CompanionBlockProbabilityTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionBlockProbability(3)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_BLOCK_PROBABILITY, 12), 36)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_BLOCK_PROBABILITY, )), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionBlockProbability)

        with self.check_changed(lambda: self.hero.companion_block_probability_multiplier):
            self.apply_ability(ability)


class HucksterTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.Huckster(buy_multiplier_left=3, buy_multiplier_right=3,
                                  sell_multiplier_left=2, sell_multiplier_right=2)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.BUY_PRICE, 12), 36)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.BUY_PRICE, MODIFIERS.SELL_PRICE)), 11), 11)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.SELL_PRICE, 12), 25)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.BUY_PRICE, MODIFIERS.SELL_PRICE)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.Huckster)

        with self.check_changed(lambda: self.hero.modify_buy_price(100)):
            with self.check_changed(lambda: self.hero.modify_sell_price(100)):
                self.apply_ability(ability)


class EtherealMagnetTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.EtherealMagnet(0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.MIGHT_CRIT_CHANCE, 0), 0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.MIGHT_CRIT_CHANCE,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.EtherealMagnet)

        with self.check_changed(lambda: self.hero.might_crit_chance):
            self.apply_ability(ability)


class CompanionTeleportTests(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionTeleport(0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_TELEPORTATOR, 0), 0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_TELEPORTATOR,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionTeleport)

        with self.check_changed(lambda: self.hero.companion_teleport_probability):
            self.apply_ability(ability)


class CompanionFly(BaseEffectsTests):

    def test_effect(self):
        effect = effects.CompanionFly(0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.COMPANION_FLYER, 0), 0.1)
        self.assertEqual(effect._modify_attribute({}, MODIFIERS.random(exclude=(MODIFIERS.COMPANION_FLYER,)), 11), 11)

    def test_in_game(self):
        ability = self.get_ability(effects.CompanionFly)

        with self.check_changed(lambda: self.hero.companion_fly_probability):
            self.apply_ability(ability)
