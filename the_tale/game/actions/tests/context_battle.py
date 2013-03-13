# coding: utf-8
import mock

from common.utils import testcase

from game.balance import constants as c

from game.actions.contexts import BattleContext, Damage

class BattleContextTest(testcase.TestCase):

    def setUp(self):
        super(BattleContextTest, self).setUp()
        self.context = BattleContext()

    def tearDown(self):
        pass


    def check_empty_values(self):
        self.assertEqual(self.context.ability_magic_mushroom, [])
        self.assertEqual(self.context.ability_sidestep, [])
        self.assertEqual(self.context.stun_length, 0)
        self.assertEqual(self.context.crit_chance, 0)
        self.assertEqual(self.context.berserk_damage_modifier, 1.0)
        self.assertEqual(self.context.ninja, 0)
        self.assertEqual(self.context.damage_queue_fire, [])
        self.assertEqual(self.context.damage_queue_poison, [])
        self.assertEqual(self.context.initiative_queue, [])

        self.assertEqual(self.context.incoming_magic_damage_modifier, 1.0)
        self.assertEqual(self.context.incoming_physic_damage_modifier, 1.0)
        self.assertEqual(self.context.outcoming_magic_damage_modifier, 1.0)
        self.assertEqual(self.context.outcoming_physic_damage_modifier, 1.0)

        self.assertEqual(self.context.pvp_advantage, 0)
        self.assertFalse(self.context.pvp_advantage_used)
        self.assertEqual(self.context.pvp_advantage_strike_damage, 0)


    def test_create(self):
        self.check_empty_values()

    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_damage(self):
        damage = Damage(100, 50)
        damage.multiply(0.5, 2)
        self.assertEqual(damage, Damage(50, 100))

        damage = Damage(100.5, 50.5)
        damage.randomize()
        self.assertEqual(damage.total, 151)

    def test_damage_queue_fire(self):
        self.assertEqual(self.context.fire_damage, None)
        self.context.use_damage_queue_fire([0])
        self.assertEqual(self.context.fire_damage, None)

        self.context.use_damage_queue_fire([10, 10, 10])
        self.assertEqual(self.context.damage_queue_fire, [0, 10, 10, 10])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_fire, [10, 10, 10])
        self.assertEqual(self.context.fire_damage, 10)

        self.context.use_damage_queue_fire([20, 10])
        self.assertEqual(self.context.damage_queue_fire, [10, 30, 20])
        self.context.on_own_turn()
        self.assertEqual(self.context.fire_damage, 30)

        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_fire, [20])
        self.assertEqual(self.context.fire_damage, 20)

        self.context.use_damage_queue_fire([1, 1, 1, 1])
        self.assertEqual(self.context.damage_queue_fire, [20, 1, 1, 1, 1])
        self.assertEqual(self.context.fire_damage, 20)
        self.context.on_own_turn()
        self.assertEqual(self.context.fire_damage, 1)

    def test_damage_queue_poison(self):
        self.assertEqual(self.context.poison_damage, None)
        self.context.use_damage_queue_poison([0])
        self.assertEqual(self.context.poison_damage, None)

        self.context.use_damage_queue_poison([10, 10, 10])
        self.assertEqual(self.context.damage_queue_poison, [0, 10, 10, 10])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [10, 10, 10])
        self.assertEqual(self.context.poison_damage, 10)

        self.context.use_damage_queue_poison([20, 10, 10])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [30, 20, 10])
        self.assertEqual(self.context.poison_damage, 30)

        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [20, 10])
        self.assertEqual(self.context.poison_damage, 20)

        self.context.use_damage_queue_poison([1, 1, 1, 1])
        self.assertEqual(self.context.damage_queue_poison, [20, 11, 1, 1, 1])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [11, 1, 1, 1])
        self.assertEqual(self.context.poison_damage, 11)

    def test_initiative_queue(self):
        self.assertEqual(self.context.initiative, 1.0)

        self.context.use_initiative([90, 90, 90, 90])
        self.context.on_own_turn()
        self.assertEqual(self.context.initiative_queue, [90, 90, 90])
        self.assertEqual(self.context.initiative, 90)

        self.context.use_initiative([11, 9])
        self.context.on_own_turn()
        self.assertEqual(self.context.initiative_queue, [810, 90])
        self.assertEqual(self.context.initiative, 810)

        self.context.on_own_turn()
        self.assertEqual(self.context.initiative_queue, [90])
        self.assertEqual(self.context.initiative, 90)

        self.context.use_initiative([10, 10, 10, 10])
        self.assertEqual(self.context.initiative_queue, [900, 10, 10, 10])
        self.context.on_own_turn()
        self.assertEqual(self.context.initiative, 10)


    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_ability_magic_mushroom(self):
        self.context.use_ability_magic_mushroom([2.0, 1.0, 0.5])
        self.assertEqual(self.context.ability_magic_mushroom, [None, 2.0, 1.0, 0.5])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [2.0, 1.0, 0.5])
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10, 5)), Damage(20, 10))

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [1.0, 0.5])
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10, 5)), Damage(10, 5))

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [0.5])
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10, 5)).total, 8)

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [])
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10, 5)), Damage(10, 5))


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

    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_modify_outcoming_damage(self):
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10, 11)).total, 21)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10.4, 11.4)).total, 22)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10.5, 11.5)).total, 22)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(10.8, 11.8)).total, 23)

        # advantage_modifier
        self.context.use_pvp_advantage(0.75)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(20, 10)).total, int(round((1+c.DAMAGE_PVP_ADVANTAGE_MODIFIER*0.75)*30)))
        self.assertFalse(self.context.pvp_advantage_used)

        self.context.use_pvp_advantage(-0.75)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(20, 10)).total, 30) # only damage from hero with heigh advantage modified
        self.assertFalse(self.context.pvp_advantage_used)

    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_modify_outcoming_damage_advantage_strike(self):
        self.context.use_pvp_advantage(1.0)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(20, 10)).total, 0) # pvp_advantage_strike_damage not set
        self.context.use_pvp_advantage_stike_damage(666)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(20, 10)).total, 666)
        self.assertTrue(self.context.pvp_advantage_used)


    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_critical_hit(self):
        old_damage = self.context.modify_outcoming_damage(Damage(100, 1000))
        self.context.use_crit_chance(100)
        new_damage = self.context.modify_outcoming_damage(Damage(100, 1000))
        self.assertTrue(old_damage.physic < new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_berserk(self):
        old_damage = self.context.modify_outcoming_damage(Damage(100, 10))
        self.context.use_berserk(1.0)
        self.assertEqual(old_damage, self.context.modify_outcoming_damage(Damage(100, 10)))
        self.context.use_berserk(1.5)
        new_damage = self.context.modify_outcoming_damage(Damage(100, 10))
        self.assertTrue(old_damage.physic < new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    def test_ninja(self):
        self.context.use_ninja(1.0)
        for i in xrange(100):
            self.assertTrue(self.context.should_miss_attack())

    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_outcoming_damage_modifier(self):
        self.assertEqual(self.context.modify_outcoming_damage(Damage(100, 1000)), Damage(100, 1000))
        self.context.use_outcoming_damage_modifier(5, 0.25)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(100, 1000)), Damage(500, 250))
        self.context.use_outcoming_damage_modifier(2, 10)
        self.assertEqual(self.context.modify_outcoming_damage(Damage(100, 1000)), Damage(1000, 2500))

    def test_incoming_damage_modifier(self):
        self.assertEqual(self.context.modify_incoming_damage(Damage(100, 1000)), Damage(100, 1000))
        self.context.use_incoming_damage_modifier(5, 0.25)
        self.assertEqual(self.context.modify_incoming_damage(Damage(100, 1000)), Damage(500, 250))
        self.context.use_incoming_damage_modifier(2, 10)
        self.assertEqual(self.context.modify_incoming_damage(Damage(100, 1000)), Damage(1000, 2500))


    def test_on_own_turn_with_empty_values(self):
        self.context.on_own_turn()
        self.check_empty_values()
