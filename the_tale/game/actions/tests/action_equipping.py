# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.actions.prototypes import ActionEquippingPrototype

from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.prototypes import TimePrototype

class ActionEquippingTest(testcase.TestCase):

    def setUp(self):
        super(ActionEquippingTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.action_equipping = ActionEquippingPrototype.create(hero=self.hero)


    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_equipping.leader, True)
        self.assertEqual(self.action_equipping.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()


    def test_processed(self):
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()


    def test_equip(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)
        artifact.power = 666

        equip_slot = artifact.type.equipment_slot
        self.hero.equipment.unequip(equip_slot)

        self.hero.bag.put_artifact(artifact)

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_equipping)
        self.assertEqual(len(self.hero.bag.items()), 0)

        equip_slot = artifact.type.equipment_slot
        self.assertEqual(self.hero.equipment.get(equip_slot), artifact)

        self.storage._test_save()


    def test_switch_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)
        artifact.power = 13

        equip_slot = artifact.type.equipment_slot

        self.hero.equipment.unequip(equip_slot)
        self.hero.equipment.equip(equip_slot, artifact)

        new_artifact = artifacts_storage.generate_artifact_from_list([artifact.record], self.hero.level+1)
        new_artifact.power = 666

        self.hero.bag.put_artifact(new_artifact)

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_equipping)

        self.assertEqual(len(self.hero.bag.items()), 1)
        self.assertEqual(self.hero.bag.items()[0][1].power, 13)

        equip_slot = artifact.type.equipment_slot

        self.assertEqual(self.hero.equipment.get(equip_slot), new_artifact)
        self.assertEqual(self.hero.equipment.get(equip_slot).power, 666)

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)


        self.storage._test_save()
