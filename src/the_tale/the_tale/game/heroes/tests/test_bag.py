# coding: utf-8
from unittest import mock

from the_tale.common.utils.testcase import TestCase

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

        account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(account)

        self.hero = self.storage.accounts_to_heroes[account.id]

        self.bag = bag.Bag()


    def test_create(self):
        self.assertEqual(self.bag.next_uuid, 0)
        self.assertEqual(self.bag.bag, {})
        self.assertEqual(self.bag._ui_info, None)


    def test_serialize(self):
        self.bag.put_artifact(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL))
        self.bag.put_artifact(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL))

        self.assertEqual(self.bag.serialize(), bag.Bag.deserialize(self.bag.serialize()).serialize())


    def test_put_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)

        self.assertEqual(artifact.bag_uuid, None)

        self.bag._ui_info = 'fake ui info'

        with self.check_delta(lambda: self.bag.occupation, 1):
            with self.check_delta(lambda: self.bag.next_uuid, 1):
                self.bag.put_artifact(artifact)

        self.assertNotEqual(artifact.bag_uuid, None)

        self.assertEqual(self.bag._ui_info, None)

        self.assertEqual(list(self.bag.bag.values())[0], artifact)

    def test_pop_artifact(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)

        self.bag.put_artifact(artifact)

        self.bag._ui_info = 'fake ui info'

        with self.check_delta(lambda: self.bag.occupation, -1):
            self.bag.pop_artifact(artifact)

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
        self.bag._ui_info = 'fake ui info'

        self.bag.mark_updated()

        self.assertEqual(self.bag._ui_info, None)


class EquipmentTests(TestCase):

    def setUp(self):
        super(EquipmentTests, self).setUp()

        create_test_map()

        account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(account)

        self.hero = self.storage.accounts_to_heroes[account.id]

        self.equipment = bag.Equipment()
        self.equipment.hero = self.hero


    def test_create(self):
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
        self.equipment._ui_info = 'fake ui info'

        self.equipment.mark_updated()

        self.assertEqual(self.equipment._ui_info, None)

    def test_get__mark_updated_called(self):
        with mock.patch('the_tale.game.heroes.bag.Equipment.mark_updated') as mark_updated:
            self.equipment.get(relations.EQUIPMENT_SLOT.PLATE)

        self.assertEqual(mark_updated.call_count, 1)


    def test_values__mark_updated_called(self):
        with mock.patch('the_tale.game.heroes.bag.Equipment.mark_updated') as mark_updated:
            list(self.equipment.values())

        self.assertEqual(mark_updated.call_count, 1)


    def test_quests_cache_reseted(self):
        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            self.equipment.mark_updated()

        self.assertEqual(mark_updated.call_count, 1)
