# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map

from game.mobs.storage import MobRecord
from game.mobs.prototypes import MobPrototype

from game.heroes.habilities import attributes

class AttributeAbiliesForHeroTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass

    def test_extra_slow(self):
        self.assertFalse(attributes.EXTRA_SLOW.AVAILABLE_TO_PLAYERS)

    def test_slow(self):
        self.assertFalse(attributes.SLOW.AVAILABLE_TO_PLAYERS)

    def test_fast(self):
        self.assertTrue(attributes.FAST.AVAILABLE_TO_PLAYERS)

        old_initiative = self.hero.initiative

        self.hero.abilities.add(attributes.FAST.get_id())

        self.assertTrue(old_initiative < self.hero.initiative)

    def test_extra_fast(self):
        self.assertFalse(attributes.EXTRA_FAST.AVAILABLE_TO_PLAYERS)


    def test_extra_thin(self):
        self.assertFalse(attributes.EXTRA_THIN.AVAILABLE_TO_PLAYERS)

    def test_thin(self):
        self.assertFalse(attributes.THIN.AVAILABLE_TO_PLAYERS)

    def test_thick(self):
        self.assertTrue(attributes.THICK.AVAILABLE_TO_PLAYERS)

        old_max_health = self.hero.max_health

        self.hero.abilities.add(attributes.THICK.get_id())

        self.assertTrue(old_max_health < self.hero.max_health)

    def test_extra_thick(self):
        self.assertFalse(attributes.EXTRA_THICK.AVAILABLE_TO_PLAYERS)


    def test_extra_weak(self):
        self.assertFalse(attributes.EXTRA_WEAK.AVAILABLE_TO_PLAYERS)

    def test_weak(self):
        self.assertFalse(attributes.WEAK.AVAILABLE_TO_PLAYERS)

    def test_strong(self):
        self.assertTrue(attributes.STRONG.AVAILABLE_TO_PLAYERS)

        old_damage_modifier = self.hero.damage_modifier

        self.hero.abilities.add(attributes.STRONG.get_id())

        self.assertTrue(old_damage_modifier < self.hero.damage_modifier)

    def test_extra_strong(self):
        self.assertFalse(attributes.EXTRA_STRONG.AVAILABLE_TO_PLAYERS)


class AttributeAbiliesForMobTest(TestCase):

    def setUp(self):
        self.mob1 = self.construct_mob_with_abilities(abilities=[attributes.EXTRA_SLOW.get_id(), attributes.EXTRA_THIN.get_id(), attributes.EXTRA_WEAK.get_id()])
        self.mob2 = self.construct_mob_with_abilities(abilities=[attributes.SLOW.get_id(), attributes.THIN.get_id(), attributes.WEAK.get_id()])
        self.mob3 = self.construct_mob_with_abilities(abilities=[attributes.FAST.get_id(), attributes.THICK.get_id(), attributes.STRONG.get_id()])
        self.mob4 = self.construct_mob_with_abilities(abilities=[attributes.EXTRA_FAST.get_id(), attributes.EXTRA_THICK.get_id(), attributes.EXTRA_STRONG.get_id()])

    @staticmethod
    def construct_mob_with_abilities(abilities):
        return MobPrototype(level=1, record=MobRecord(level=1, id='test_mob', name='', normalized_name='', morph='', abilities=abilities, terrain=[], loot=[], artifacts=[]))

    def tearDown(self):
        pass

    def test_slow_fast(self):
        self.assertTrue(self.mob1.initiative < self.mob2.initiative < self.mob3.initiative < self.mob4.initiative)

    def test_thin_thick(self):
        self.assertTrue(self.mob1.max_health < self.mob2.max_health < self.mob3.max_health < self.mob4.max_health)

    def test_weak_strong(self):
        self.assertTrue(self.mob1.damage_modifier < self.mob2.damage_modifier < self.mob3.damage_modifier < self.mob4.damage_modifier)
