# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.map.relations import TERRAIN
from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.heroes.relations import ARCHETYPE

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs.relations import MOB_RECORD_STATE, MOB_TYPE
from the_tale.game.mobs.prototypes import MobPrototype, MobRecordPrototype
from the_tale.game.mobs.forms import ModerateMobRecordForm
from the_tale.game.mobs import exceptions

from the_tale.linguistics.tests import helpers as linguistics_helpers


class MobsPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(MobsPrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

        mobs_storage.sync(force=True)

    def test_serialization(self):
        mob = mobs_storage.all()[0].create_mob(self.hero)
        self.assertEqual(mob, MobPrototype.deserialize(mob.serialize()))

    def test_deserialization_of_disabled_mob(self):
        mob_record = mobs_storage.all()[0]
        mob = mob_record.create_mob(self.hero)

        data = mob.serialize()

        mob_record.state = MOB_RECORD_STATE.DISABLED
        mob_record.save()

        mob_2 = MobPrototype.deserialize(data)

        self.assertNotEqual(mob.id, mob_2.id)


    def test_load_data(self):
        self.assertEqual(len(mobs_storage.all()), 3) # create_test_map create 3 random mobs
        self.assertFalse(mobs_storage.has_mob('wrong_id'))
        self.assertTrue(mobs_storage.has_mob('mob_1'))
        self.assertTrue(mobs_storage.has_mob('mob_2'))
        self.assertTrue(mobs_storage.has_mob('mob_3'))

    def test_storage_version_update_on_create(self):
        old_version = mobs_storage.version
        MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.assertNotEqual(old_version, mobs_storage.version)

    def test_storage_version_update_on_save(self):
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        old_version = mobs_storage.version
        mob.save()
        self.assertNotEqual(old_version, mobs_storage.version)

    def test_mob_attributes(self):
        MobRecordPrototype.create(uuid='bandit',
                                  level=1,
                                  utg_name=names.generator.get_test_name(name='bandit'),
                                  description='bandint',
                                  abilities=['hit', 'thick', 'slow', 'extra_strong'],
                                  terrains=TERRAIN.records,
                                  type=MOB_TYPE.CIVILIZED,
                                  archetype=ARCHETYPE.NEUTRAL,
                                  state=MOB_RECORD_STATE.ENABLED)
        mobs_storage.sync(force=True)

        bandit = MobPrototype(record=mobs_storage.get_by_uuid('bandit'), level=1)

        self.assertEqual(bandit.health_cooficient, 1.025)
        self.assertEqual(bandit.initiative, 0.975)
        self.assertEqual(bandit.damage_modifier, 1.05)

    def test_save__not_stored_mob(self):
        mob = MobRecordPrototype.get_by_id(mobs_storage.all()[0].id)

        self.assertRaises(exceptions.SaveNotRegisteredMobError, mob.save)
