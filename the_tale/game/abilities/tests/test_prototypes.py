# coding: utf-8
import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.postponed_tasks import ComplexChangeTask

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

    def test_process_no_energy(self):
        self.hero._model.energy = 0
        self.hero._model.energy_bonus = 0
        self.hero.save()
        self.assertFalse(self.ability.check_hero_conditions(self.hero))

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.energy_discount', 1)
    def test_process_energy_discount(self):
        self.hero._model.energy = ABILITY_TYPE.HELP.cost - 1
        self.hero._model.energy_bonus = 0
        self.hero.save()
        self.assertTrue(self.ability.check_hero_conditions(self.hero))

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.energy_discount', 1)
    def test_process_energy_discount__no_energy(self):
        self.hero._model.energy = ABILITY_TYPE.HELP.cost - 2
        self.hero._model.energy_bonus = 0
        self.hero.save()

        self.assertFalse(self.ability.check_hero_conditions(self.hero))


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.energy_discount', 100)
    def test_process_energy_discount__limit_1(self):
        self.hero._model.energy = 2
        self.hero._model.energy_bonus = 0
        self.hero.save()


        self.assertTrue(self.ability.check_hero_conditions(self.hero))

        self.ability.hero_actions(self.hero)

        self.assertEqual(self.hero.energy, 1)


    def test_process_bonus_energy(self):
        self.hero._model.energy = 0
        self.hero.add_energy_bonus(100)
        self.hero.save()

        self.assertTrue(self.ability.check_hero_conditions(self.hero))


    def test_process_energy(self):
        self.hero._model.energy = self.hero.energy_maximum
        self.hero.save()

        self.assertTrue(self.ability.check_hero_conditions(self.hero))

        self.ability.hero_actions(self.hero)

        self.assertTrue(self.hero.energy < self.hero.energy_maximum)
