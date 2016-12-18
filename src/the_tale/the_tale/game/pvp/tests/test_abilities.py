# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.pvp.abilities import Ice, Blood, Flame

from the_tale.game.actions import meta_actions
from the_tale.game.actions import prototypes as actions_prototypes


class AbilitiesTests(testcase.TestCase):

    def setUp(self):
        super(AbilitiesTests, self).setUp()

        create_test_map()

        account_1 = self.accounts_factory.create_account()
        account_2 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(account_1)
        self.storage.load_account_data(account_2)

        self.hero = self.storage.accounts_to_heroes[account_1.id]
        self.enemy = self.storage.accounts_to_heroes[account_2.id]

        self.meta_action_battle = meta_actions.ArenaPvP1x1.create(self.storage, self.hero, self.enemy)
        self.meta_action_battle.set_storage(self.storage)

        actions_prototypes.ActionMetaProxyPrototype.create(hero=self.hero, _bundle_id=self.hero.actions.current_action.bundle_id, meta_action=self.meta_action_battle)
        actions_prototypes.ActionMetaProxyPrototype.create(hero=self.enemy, _bundle_id=self.hero.actions.current_action.bundle_id, meta_action=self.meta_action_battle)


    def test_ice_apply(self):
        self.assertEqual(self.meta_action_battle.hero_1_pvp.energy_speed, 1)
        ability = Ice(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertTrue(self.meta_action_battle.hero_1_pvp.energy_speed > 1)

    def test_flame_apply_minimum(self):
        self.assertEqual(self.meta_action_battle.hero_2_pvp.energy_speed, 1)
        ability = Flame(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertEqual(self.meta_action_battle.hero_2_pvp.energy_speed, 1)

    def test_flame_apply(self):
        self.meta_action_battle.hero_2_pvp.set_energy_speed(100)
        ability = Flame(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertTrue(self.meta_action_battle.hero_2_pvp.energy_speed < 100)

    def test_blood_apply(self):
        self.meta_action_battle.hero_1_pvp.set_effectiveness(0)
        ability = Blood(hero=self.hero, enemy=self.enemy)
        ability.apply()
        self.assertEqual(self.meta_action_battle.hero_1_pvp.effectiveness,  0)

        self.meta_action_battle.hero_1_pvp.set_energy(1)
        ability.apply()
        self.assertTrue(self.meta_action_battle.hero_1_pvp.effectiveness > 0)


    def test_blood_apply__with_might(self):
        self.meta_action_battle.hero_1_pvp.set_effectiveness(0)
        self.meta_action_battle.hero_1_pvp.set_energy(1000)

        ability = Blood(hero=self.hero, enemy=self.enemy)
        ability.apply()

        clean_effectiveness = self.meta_action_battle.hero_1_pvp.effectiveness

        self.meta_action_battle.hero_1_pvp.set_energy(1000)
        self.hero.might = 10000
        self.meta_action_battle.hero_1_pvp.set_effectiveness(0)
        ability = Blood(hero=self.hero, enemy=self.enemy)
        ability.apply()

        self.assertTrue(clean_effectiveness < self.meta_action_battle.hero_1_pvp.effectiveness)
