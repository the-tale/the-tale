# coding: utf-8
import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.abilities.relations import ABILITY_TYPE
from the_tale.game.abilities.deck import ABILITIES

ABILITY_TASK_STATE = ComplexChangeTask


class PrototypesTests(TestCase):

    def setUp(self):
        super(PrototypesTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = ABILITIES[ABILITY_TYPE.HELP]()

        self.task_data = {}

    def test_process_no_energy(self):
        self.hero.energy = 0
        self.hero.energy_bonus = 0
        heroes_logic.save_hero(self.hero)
        self.assertFalse(self.ability.check_hero_conditions(self.hero, self.task_data))

    @mock.patch('the_tale.game.abilities.relations.ABILITY_TYPE.HELP.cost', 0)
    def test_process_no_energy__no_cost(self):
        self.hero.energy = 0
        self.hero.energy_bonus = 0
        heroes_logic.save_hero(self.hero)
        self.assertTrue(self.ability.check_hero_conditions(self.hero, self.task_data))

    @mock.patch('the_tale.game.heroes.objects.Hero.energy_discount', 1)
    def test_process_energy_discount(self):
        self.hero.energy = ABILITY_TYPE.HELP.cost - 1
        self.hero.energy_bonus = 0
        heroes_logic.save_hero(self.hero)
        self.assertTrue(self.ability.check_hero_conditions(self.hero, self.task_data))

    @mock.patch('the_tale.game.heroes.objects.Hero.energy_discount', 1)
    def test_process_energy_discount__no_energy(self):
        self.hero.energy = ABILITY_TYPE.HELP.cost - 2
        self.hero.energy_bonus = 0
        heroes_logic.save_hero(self.hero)

        self.assertFalse(self.ability.check_hero_conditions(self.hero, self.task_data))


    @mock.patch('the_tale.game.heroes.objects.Hero.energy_discount', 100)
    def test_process_energy_discount__limit_1(self):
        self.hero.energy = 2
        self.hero.energy_bonus = 0
        heroes_logic.save_hero(self.hero)

        self.assertTrue(self.ability.check_hero_conditions(self.hero, self.task_data))

        self.ability.hero_actions(self.hero, self.task_data)

        self.assertEqual(self.hero.energy, 1)


    def test_process_bonus_energy(self):
        self.hero.energy = 0
        self.hero.add_energy_bonus(100)
        heroes_logic.save_hero(self.hero)

        self.assertTrue(self.ability.check_hero_conditions(self.hero, self.task_data))


    def test_process_energy(self):
        self.hero.energy = self.hero.energy_maximum
        heroes_logic.save_hero(self.hero)

        self.assertTrue(self.ability.check_hero_conditions(self.hero, self.task_data))

        self.ability.hero_actions(self.hero, self.task_data)

        self.assertTrue(self.hero.energy < self.hero.energy_maximum)
