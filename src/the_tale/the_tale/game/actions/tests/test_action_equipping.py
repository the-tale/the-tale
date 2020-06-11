
import smart_imports

smart_imports.all()


class ActionEquippingTest(utils_testcase.TestCase):

    def setUp(self):
        super(ActionEquippingTest, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account.id)
        self.hero = self.storage.accounts_to_heroes[account.id]
        self.action_idl = self.hero.actions.current_action

        self.action_equipping = prototypes.ActionEquippingPrototype.create(hero=self.hero)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_equipping.leader, True)
        self.assertEqual(self.action_equipping.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_equip(self):
        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = power.Power(666, 666)

        equip_slot = artifact.type.equipment_slot
        self.hero.equipment.unequip(equip_slot)

        self.hero.bag.put_artifact(artifact)

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_equipping)
        self.assertEqual(len(list(self.hero.bag.items())), 0)

        equip_slot = artifact.type.equipment_slot
        self.assertEqual(self.hero.equipment.get(equip_slot), artifact)

        self.storage._test_save()

    def test_switch_artifact(self):
        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL)
        artifact.power = power.Power(13, 13)

        equip_slot = artifact.type.equipment_slot

        self.hero.equipment.unequip(equip_slot)
        self.hero.equipment.equip(equip_slot, artifact)

        new_artifact = artifacts_storage.artifacts.generate_artifact_from_list([artifact.record], self.hero.level + 1, rarity=artifacts_relations.RARITY.NORMAL)
        new_artifact.power = power.Power(666, 666)

        self.hero.bag.put_artifact(new_artifact)

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_equipping)

        self.assertEqual(len(list(self.hero.bag.items())), 1)
        self.assertEqual(list(self.hero.bag.items())[0][1].power, power.Power(13, 13))

        equip_slot = artifact.type.equipment_slot

        self.assertEqual(self.hero.equipment.get(equip_slot), new_artifact)
        self.assertEqual(self.hero.equipment.get(equip_slot).power, power.Power(666, 666))

        game_turn.increment()

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage._test_save()
