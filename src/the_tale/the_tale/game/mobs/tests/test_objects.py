
import smart_imports

smart_imports.all()


class MobsPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(MobsPrototypeTests, self).setUp()
        game_logic.create_test_map()

        account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=account.id)

        storage.mobs.sync(force=True)

    def test_serialization(self):
        mob = storage.mobs.all()[0].create_mob(self.hero)
        self.assertEqual(mob, objects.Mob.deserialize(mob.serialize()))

    def test_deserialization_of_disabled_mob(self):
        mob_record = storage.mobs.all()[0]
        mob = mob_record.create_mob(self.hero)

        data = mob.serialize()

        mob_record.state = relations.MOB_RECORD_STATE.DISABLED
        logic.save_mob_record(mob_record)

        mob_2 = objects.Mob.deserialize(data)

        self.assertNotEqual(mob.id, mob_2.id)

    def test_load_data(self):
        self.assertEqual(len(storage.mobs.all()), 3)  # create_test_map create 3 random mobs
        self.assertFalse(storage.mobs.has_mob('wrong_id'))
        self.assertTrue(storage.mobs.has_mob('mob_1'))
        self.assertTrue(storage.mobs.has_mob('mob_2'))
        self.assertTrue(storage.mobs.has_mob('mob_3'))

    def test_storage_version_update_on_create(self):
        old_version = storage.mobs.version
        logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.assertNotEqual(old_version, storage.mobs.version)

    def test_linguistics_restrictions_on_create(self):
        with mock.patch('the_tale.linguistics.logic.sync_restriction') as sync_restriction:
            mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)

        self.assertEqual(sync_restriction.call_args_list, [mock.call(group=linguistics_restrictions.GROUP.MOB,
                                                                     external_id=mob.id,
                                                                     name=mob.name)])

    def test_storage_version_update_on_save(self):
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        old_version = storage.mobs.version
        logic.save_mob_record(mob)
        self.assertNotEqual(old_version, storage.mobs.version)

    def test_linguistics_restrictions_update_on_save(self):
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        mob.set_utg_name(game_names.generator().get_test_name('new-name'))

        with mock.patch('the_tale.linguistics.logic.sync_restriction') as sync_restriction:
            logic.save_mob_record(mob)

        self.assertEqual(sync_restriction.call_args_list, [mock.call(group=linguistics_restrictions.GROUP.MOB,
                                                                     external_id=mob.id,
                                                                     name=mob.name)])

    def test_mob_attributes(self):
        logic.create_random_mob_record(uuid='bandit',
                                       level=1,
                                       utg_name=game_names.generator().get_test_name(name='bandit'),
                                       description='bandint',
                                       abilities=['hit', 'thick', 'slow', 'extra_strong'],
                                       terrains=map_relations.TERRAIN.records,
                                       type=tt_beings_relations.TYPE.CIVILIZED,
                                       archetype=game_relations.ARCHETYPE.NEUTRAL,
                                       state=relations.MOB_RECORD_STATE.ENABLED)
        storage.mobs.sync(force=True)

        bandit = objects.Mob(record_id=storage.mobs.get_by_uuid('bandit').id, level=1)

        self.assertEqual(bandit.health_cooficient, 1.025)
        self.assertEqual(bandit.initiative, 0.975)
        self.assertEqual(bandit.damage_modifier, 1.05)

    def test_save__not_stored_mob(self):
        model = models.MobRecord.objects.get(id=storage.mobs.all()[0].id)

        mob = logic.construct_from_model(model)

        self.assertRaises(exceptions.SaveNotRegisteredMobError, logic.save_mob_record, mob)
