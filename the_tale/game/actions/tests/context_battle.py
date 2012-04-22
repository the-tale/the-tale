# coding: utf-8

from django.test import TestCase

from game.actions.contexts import BattleContext

class BattleContextTest(TestCase):

    def setUp(self):
        self.context = BattleContext()

    def tearDown(self):
        pass


    def check_empty_values(self):
        self.assertEqual(self.context.ability_magic_mushroom, [])
        self.assertEqual(self.context.ability_sidestep, [])
        self.assertEqual(self.context.stun_length, 0)


    def test_create(self):
        self.check_empty_values()


    def test_ability_magic_mushroom(self):
        self.context.use_ability_magic_mushroom([2.0, 1.0, 0.5])
        self.assertEqual(self.context.ability_magic_mushroom, [None, 2.0, 1.0, 0.5])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [2.0, 1.0, 0.5])
        self.assertEqual(self.context.modify_initial_damage(1), 2.0)

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [1.0, 0.5])
        self.assertEqual(self.context.modify_initial_damage(1), 1.0)

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [0.5])
        self.assertEqual(self.context.modify_initial_damage(1), 0.5)

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [])
        self.assertEqual(self.context.modify_initial_damage(1), 1)


    def test_ability_sidestep(self):
        self.context.use_ability_sidestep([1.0, 0.5, 0.0])
        self.assertEqual(self.context.ability_sidestep, [None, 1.0, 0.5, 0])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [1.0, 0.5, 0])
        self.assertTrue(self.context.should_miss_attack())

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [0.5, 0])
        self.assertTrue(self.context.should_miss_attack() in [True, False])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [0])
        self.assertTrue(not self.context.should_miss_attack())

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [])
        self.assertTrue(not self.context.should_miss_attack())


    def test_stun(self):
        self.context.use_stun(3)
        self.assertEqual(self.context.stun_length, 4)

        # longes stun must be used
        self.context.use_stun(1)
        self.assertEqual(self.context.stun_length, 4)

        for i in xrange(3):
            self.context.on_own_turn()
            self.assertEqual(self.context.stun_length, 3-i)
            self.assertTrue(self.context.is_stunned)

        self.context.on_own_turn()
        self.assertEqual(self.context.stun_length, 0)
        self.assertTrue(not self.context.is_stunned)


    def test_on_own_turn_with_empty_values(self):
        self.context.on_own_turn()
        self.check_empty_values()
