# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.pvp.abilities import Ice, Blood, Flame


class AbilitiesTests(testcase.TestCase):

    def setUp(self):
        super(AbilitiesTests, self).setUp()

        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        result, account_1_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.hero = heroes_logic.load_hero(account_id=account_1_id)
        self.enemy = heroes_logic.load_hero(account_id=account_1_id)

    def test_ice_apply(self):
        self.assertEqual(self.hero.pvp.energy_speed, 1)
        ability = Ice(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertTrue(self.hero.pvp.energy_speed > 1)

    def test_flame_apply_minimum(self):
        self.assertEqual(self.enemy.pvp.energy_speed, 1)
        ability = Flame(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertEqual(self.enemy.pvp.energy_speed, 1)

    def test_flame_apply(self):
        self.enemy.pvp.set_energy_speed(100)
        ability = Flame(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertTrue(self.enemy.pvp.energy_speed < 100)

    def test_blood_apply(self):
        self.assertEqual(self.hero.pvp.effectiveness, 0)
        ability = Blood(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertEqual(self.hero.pvp.effectiveness,  0)

        self.hero.pvp.set_energy(1)
        ability.apply()
        self.assertTrue(self.hero.pvp.effectiveness > 0)


    def test_blood_apply__with_might(self):
        self.hero.pvp.set_energy(1000)
        self.assertEqual(self.hero.pvp.effectiveness, 0)
        ability = Blood(hero=self.hero, enemy=self.enemy)
        ability.apply()

        clean_effectiveness = self.hero.pvp.effectiveness

        self.hero.pvp.set_energy(1000)
        self.hero.might = 10000
        self.hero.pvp.set_effectiveness(0)
        ability = Blood(hero=self.hero, enemy=self.enemy)
        ability.apply()

        self.assertTrue(clean_effectiveness < self.hero.pvp.effectiveness)
