# coding: utf-8
from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.relations import RARITY

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes import bag
from the_tale.game.heroes import relations


class BagTests(TestCase):

    def setUp(self):
        super(BagTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        self.hero = self.storage.accounts_to_heroes[account_id]

        self.bag = bag.Bag()


    def test_create(self):
        self.assertEqual(self.bag.next_uuid, 0)
        self.assertEqual(self.bag.updated, True)
        self.assertEqual(self.bag.bag, {})
        self.assertEqual(self.bag._ui_info, None)


    def test_serialize(self):
        self.bag.put_artifact(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL))
        self.bag.put_artifact(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL))

        self.assertEqual(self.bag.serialize(), bag.Bag.deserialize(self.bag.serialize()).serialize())


    def test_put_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)

        self.assertEqual(artifact.bag_uuid, None)

        self.bag.updated = False
        self.bag._ui_info = 'fake ui info'

        with self.check_delta(lambda: self.bag.occupation, 1):
            with self.check_delta(lambda: self.bag.next_uuid, 1):
                self.bag.put_artifact(artifact)

        self.assertNotEqual(artifact.bag_uuid, None)

        self.assertTrue(self.bag.updated)
        self.assertEqual(self.bag._ui_info, None)

        self.assertEqual(self.bag.bag.values()[0], artifact)

    def test_pop_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)

        self.bag.put_artifact(artifact)

        self.bag.updated = False
        self.bag._ui_info = 'fake ui info'

        with self.check_delta(lambda: self.bag.occupation, -1):
            self.bag.pop_artifact(artifact)

        self.assertTrue(self.bag.updated)
        self.assertEqual(self.bag._ui_info, None)

        self.assertEqual(self.bag.bag, {})


    def test_ui_info_cache(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)

        self.bag.put_artifact(artifact)

        ui_info = self.bag.ui_info(self.hero)

        self.assertEqual(self.bag._ui_info, ui_info)

        self.bag.mark_updated()

        self.assertEqual(self.bag._ui_info, None)


    def test_mark_updated(self):
        self.bag.updated = False
        self.bag._ui_info = 'fake ui info'

        self.bag.mark_updated()

        self.assertTrue(self.bag.updated)
        self.assertEqual(self.bag._ui_info, None)


class EquipmentTests(TestCase):

    def setUp(self):
        super(EquipmentTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        self.hero = self.storage.accounts_to_heroes[account_id]

        self.equipment = bag.Equipment()
        self.equipment.hero = self.hero


    def test_create(self):
        self.assertEqual(self.equipment.updated, True)
        self.assertEqual(self.equipment.equipment, {})
        self.assertEqual(self.equipment._ui_info, None)


    def test_serialize(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)
        self.equipment.equip(artifact.type.equipment_slot, artifact)

        self.assertEqual(self.equipment.serialize(), bag.Equipment.deserialize(self.equipment.serialize()).serialize())


    def test_ui_info_cache(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)
        self.equipment.equip(artifact.type.equipment_slot, artifact)

        ui_info = self.equipment.ui_info(self.hero)

        self.assertEqual(self.equipment._ui_info, ui_info)

        self.equipment.mark_updated()

        self.assertEqual(self.equipment._ui_info, None)

    def test_mark_updated(self):
        self.equipment.updated = False
        self.equipment._ui_info = 'fake ui info'

        self.equipment.mark_updated()

        self.assertTrue(self.equipment.updated)
        self.assertEqual(self.equipment._ui_info, None)

    def test_get__mark_updated_called(self):
        self.equipment.updated = False

        self.equipment.get(relations.EQUIPMENT_SLOT.PLATE)

        self.assertTrue(self.equipment.updated)

    def test_values__mark_updated_called(self):
        self.equipment.updated = False

        self.equipment.values()

        self.assertTrue(self.equipment.updated)


    def test_quests_cache_reseted(self):
        self.hero.quests.updated = False

        self.equipment.mark_updated()

        self.assertTrue(self.hero.quests.updated)
