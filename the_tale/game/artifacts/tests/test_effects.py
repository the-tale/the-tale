# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.artifacts import relations
from the_tale.game.artifacts import effects
from the_tale.game.artifacts.storage import artifacts_storage


class EffectsTests(testcase.TestCase):

    def setUp(self):
        super(EffectsTests, self).setUp()

        create_test_map()

        account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=account.id)

        artifacts_storage.sync(force=True)

        self.artifact = self.hero.equipment.values()[0]


    def test_all_effects_declared(self):
        for effect in relations.ARTIFACT_EFFECT.records:
            self.assertTrue(effect in effects.EFFECTS)


    def test_no_undeclared_effects(self):
        for effect in effects.EFFECTS.values():
            self.assertTrue(effect.TYPE in relations.ARTIFACT_EFFECT.records)

    def _set_effect(self, effect):
        self.artifact.rarity = relations.RARITY.RARE
        self.artifact.record.rare_effect = effect
        self.hero.reset_accessors_cache()

    def test_physical_damage(self):
        old_damage = self.hero.basic_damage
        self._set_effect(relations.ARTIFACT_EFFECT.PHYSICAL_DAMAGE)
        new_damage = self.hero.basic_damage
        self.assertEqual(old_damage.magic, new_damage.magic)
        self.assertTrue(old_damage.physic < new_damage.physic)

    def test_magical_damage(self):
        old_damage = self.hero.basic_damage
        self._set_effect(relations.ARTIFACT_EFFECT.MAGICAL_DAMAGE)
        new_damage = self.hero.basic_damage
        self.assertEqual(old_damage.physic, new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    def test_initiative(self):
        with self.check_increased(lambda: self.hero.initiative):
            self._set_effect(relations.ARTIFACT_EFFECT.INITIATIVE)

    def test_health(self):
        with self.check_increased(lambda: self.hero.max_health):
            self._set_effect(relations.ARTIFACT_EFFECT.HEALTH)

    def test_experience(self):
        with self.check_increased(lambda: self.hero.experience_modifier):
            self._set_effect(relations.ARTIFACT_EFFECT.EXPERIENCE)

    def test_power(self):
        with self.check_increased(lambda: self.hero.politics_power_modifier):
            self._set_effect(relations.ARTIFACT_EFFECT.POWER)

    def test_speed(self):
        with self.check_increased(lambda: self.hero.move_speed):
            self._set_effect(relations.ARTIFACT_EFFECT.SPEED)

    def test_bag(self):
        with self.check_increased(lambda: self.hero.max_bag_size):
            self._set_effect(relations.ARTIFACT_EFFECT.BAG)


    def test_great_physical_damage(self):
        old_damage = self.hero.basic_damage
        self._set_effect(relations.ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE)
        new_damage = self.hero.basic_damage
        self.assertEqual(old_damage.magic, new_damage.magic)
        self.assertTrue(old_damage.physic < new_damage.physic)

    def test_great_magical_damage(self):
        old_damage = self.hero.basic_damage
        self._set_effect(relations.ARTIFACT_EFFECT.GREAT_MAGICAL_DAMAGE)
        new_damage = self.hero.basic_damage
        self.assertEqual(old_damage.physic, new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    def test_great_initiative(self):
        with self.check_increased(lambda: self.hero.initiative):
            self._set_effect(relations.ARTIFACT_EFFECT.GREAT_INITIATIVE)

    def test_great_health(self):
        with self.check_increased(lambda: self.hero.max_health):
            self._set_effect(relations.ARTIFACT_EFFECT.GREAT_HEALTH)

    def test_great_experience(self):
        with self.check_increased(lambda: self.hero.experience_modifier):
            self._set_effect(relations.ARTIFACT_EFFECT.GREAT_EXPERIENCE)

    def test_great_power(self):
        with self.check_increased(lambda: self.hero.politics_power_modifier):
            self._set_effect(relations.ARTIFACT_EFFECT.GREAT_POWER)

    def test_great_speed(self):
        with self.check_increased(lambda: self.hero.move_speed):
            self._set_effect(relations.ARTIFACT_EFFECT.GREAT_SPEED)

    def test_great_bag(self):
        with self.check_increased(lambda: self.hero.max_bag_size):
            self._set_effect(relations.ARTIFACT_EFFECT.GREAT_BAG)

    def test_rest_length(self):
        with self.check_decreased(lambda: self.hero.rest_length):
            self._set_effect(relations.ARTIFACT_EFFECT.REST_LENGTH)

    def test_resurrect_length(self):
        with self.check_decreased(lambda: self.hero.resurrect_length):
            self._set_effect(relations.ARTIFACT_EFFECT.RESURRECT_LENGTH)

    def test_idel_length(self):
        with self.check_decreased(lambda: self.hero.idle_length):
            self._set_effect(relations.ARTIFACT_EFFECT.IDLE_LENGTH)

    def test_conviction(self):
        with self.check_decreased(self.hero.buy_price):
            self._set_effect(relations.ARTIFACT_EFFECT.CONVICTION)

    def test_charm(self):
        with self.check_increased(self.hero.sell_price):
            self._set_effect(relations.ARTIFACT_EFFECT.CHARM)

    def test_spiritual_connection(self):
        with self.check_increased(lambda: self.hero.energy_discount):
            self._set_effect(relations.ARTIFACT_EFFECT.SPIRITUAL_CONNECTION)

    def test_peace_of_mind(self):
        with self.check_increased(lambda: self.hero.regenerate_double_energy_probability):
            self._set_effect(relations.ARTIFACT_EFFECT.PEACE_OF_MIND)

    def test_special_aura(self):
        with self.check_increased(lambda: self.hero.bonus_artifact_power.total()):
            self._set_effect(relations.ARTIFACT_EFFECT.SPECIAL_AURA)

    def test_last_chance(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.LAST_CHANCE)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.LastChance.ABILITY)

    def test_regeneration(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.REGENERATION)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.Regeneration.ABILITY)

    def test_ice(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.ICE)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.Ice.ABILITY)

    def test_recklessness(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.RECKLESSNESS)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.Recklessness.ABILITY)

    def test_flame(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.FLAME)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.Flame.ABILITY)

    def test_poison(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.POISON)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.Poison.ABILITY)

    def test_vampire_strike(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.VAMPIRE_STRIKE)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.VampireStrike.ABILITY)

    def test_speedup(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.SPEEDUP)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.Speedup.ABILITY)

    def test_critical_hit(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.CRITICAL_HIT)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.CriticalHit.ABILITY)

    def test_astral_barrier(self):
        self.assertEqual(self.hero.additional_abilities, [])
        self._set_effect(relations.ARTIFACT_EFFECT.ASTRAL_BARRIER)
        self.assertEqual(len(self.hero.additional_abilities), 1)
        self.assertEqual(self.hero.additional_abilities[0].__class__, effects.AstralBarrier.ABILITY)

    def test_esprit(self):
        with self.check_decreased(lambda: self.hero.preferences_change_delay):
            self._set_effect(relations.ARTIFACT_EFFECT.ESPRIT)

    def test_terrible_view(self):
        with self.check_increased(lambda: self.hero.leave_battle_in_fear_probability):
            self._set_effect(relations.ARTIFACT_EFFECT.TERRIBLE_VIEW)

    def test_clouded_mind(self):
        self.assertFalse(self.hero.clouded_mind)
        self._set_effect(relations.ARTIFACT_EFFECT.CLOUDED_MIND)
        self.assertTrue(self.hero.clouded_mind)

    def test_luck_of_stranger(self):
        with self.check_increased(lambda: self.hero.rare_artifact_probability_multiplier):
            self._set_effect(relations.ARTIFACT_EFFECT.LUCK_OF_STRANGER)

    def test_luck_of_hero(self):
        with self.check_increased(lambda: self.hero.epic_artifact_probability_multiplier):
            self._set_effect(relations.ARTIFACT_EFFECT.LUCK_OF_HERO)

    def test_ideological(self):
        with self.check_increased(lambda: self.hero.habits_increase_modifier):
            self._set_effect(relations.ARTIFACT_EFFECT.IDEOLOGICAL)

    def test_fortitude(self):
        with self.check_decreased(lambda: self.hero.habits_decrease_modifier):
            self._set_effect(relations.ARTIFACT_EFFECT.FORTITUDE)

    def test_unbreakable(self):
        with self.check_increased(lambda: self.hero.safe_artifact_integrity_probability):
            self._set_effect(relations.ARTIFACT_EFFECT.UNBREAKABLE)

    def test_no_effect(self):
        with self.check_not_changed(lambda: effects.EFFECTS[self.artifact.record.rare_effect].modify_attribute(None, 100)):
            self._set_effect(relations.ARTIFACT_EFFECT.NO_EFFECT)
