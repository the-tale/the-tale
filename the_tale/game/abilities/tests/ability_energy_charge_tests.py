# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map


from the_tale.game.abilities.deck import EnergyCharge
from the_tale.game.abilities.relations import ABILITY_TYPE, ABILITY_RESULT


class EnergyChargeAbilityTest(testcase.TestCase):

    def setUp(self):
        super(EnergyChargeAbilityTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.hero._model.energy = 0
        self.hero.energy_charges = 0

        self.ability = EnergyCharge()

    @property
    def use_attributes(self):
        return {'data': {'hero_id': self.hero.id},
                'step': None,
                'main_task_id': 0,
                'storage': self.storage,
                'pvp_balancer': None}

    def test_no_charges(self):
        self.assertEqual(self.ability.use(**self.use_attributes), (ABILITY_RESULT.FAILED, None, ()))
        self.assertEqual(self.hero.energy, 0)
        self.assertEqual(self.hero.energy_charges, 0)

    def test_to_many_energy(self):
        self.hero._model.energy = ABILITY_TYPE.HELP.cost
        self.hero.energy_charges = 2
        self.assertEqual(self.ability.use(**self.use_attributes), (ABILITY_RESULT.FAILED, None, ()))
        self.assertEqual(self.hero.energy, ABILITY_TYPE.HELP.cost)
        self.assertEqual(self.hero.energy_charges, 2)

    def test_success(self):
        self.hero.energy_charges = 2
        self.assertEqual(self.ability.use(**self.use_attributes), (ABILITY_RESULT.SUCCESSED, None, ()))
        self.assertEqual(self.hero.energy, self.hero.energy_maximum)
        self.assertEqual(self.hero.energy_charges, 1)
