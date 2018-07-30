
import smart_imports

smart_imports.all()


class ArtifactTests(utils_testcase.TestCase):

    def setUp(self):
        super(ArtifactTests, self).setUp()
        game_logic.create_test_map()

        account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=account.id)

        storage.artifacts.sync(force=True)

        self.artifact_record = storage.artifacts.all()[0]

    def test_serialization(self):
        artifact = storage.artifacts.all()[0].create_artifact(level=6, power=power.Power(1, 100))
        self.assertEqual(artifact, objects.Artifact.deserialize(artifact.serialize()))

    def test_deserialization_of_disabled_artifact(self):
        artifact_record = storage.artifacts.all()[0]
        artifact = artifact_record.create_artifact(level=7, power=power.Power(1, 1))

        data = artifact.serialize()

        artifact_record.state = relations.ARTIFACT_RECORD_STATE.DISABLED
        logic.save_artifact_record(artifact_record)

        for i in range(1000):
            artifact_2 = objects.Artifact.deserialize(data)
            self.assertNotEqual(artifact.id, artifact_2.id)

    def test_load_data(self):
        self.assertEqual(len(storage.artifacts.all()), 11)  # see create_test_map
        self.assertFalse(storage.artifacts.has_artifact('wrong_id'))
        self.assertTrue(storage.artifacts.has_artifact('loot_1'))
        self.assertTrue(storage.artifacts.has_artifact('loot_2'))
        self.assertTrue(storage.artifacts.has_artifact('loot_3'))
        self.assertTrue(storage.artifacts.has_artifact('helmet_1'))
        self.assertTrue(storage.artifacts.has_artifact('plate_1'))
        self.assertTrue(storage.artifacts.has_artifact('boots_1'))

    def test_storage_version_update_on_create(self):
        old_version = storage.artifacts.version
        logic.create_random_artifact_record(uuid='bandit_loot')
        self.assertNotEqual(old_version, storage.artifacts.version)

    def test_linguistics_restriction_on_create(self):
        with mock.patch('the_tale.linguistics.logic.sync_restriction') as sync_restriction:
            artifact = logic.create_random_artifact_record(uuid='bandit_loot')

        self.assertEqual(sync_restriction.call_args_list, [mock.call(group=linguistics_restrictions.GROUP.ARTIFACT,
                                                                     external_id=artifact.id,
                                                                     name=artifact.name)])

    def test_storage_version_update_on_save(self):
        artifact = logic.create_random_artifact_record(uuid='bandit_loot')
        old_version = storage.artifacts.version
        logic.save_artifact_record(artifact)
        self.assertNotEqual(old_version, storage.artifacts.version)

    def test_linguistics_restriction_version_update_on_save(self):
        artifact = logic.create_random_artifact_record(uuid='bandit_loot')
        artifact.set_utg_name(game_names.generator().get_test_name('new-name'))

        with mock.patch('the_tale.linguistics.logic.sync_restriction') as sync_restriction:
            logic.save_artifact_record(artifact)

        self.assertEqual(sync_restriction.call_args_list, [mock.call(group=linguistics_restrictions.GROUP.ARTIFACT,
                                                                     external_id=artifact.id,
                                                                     name=artifact.name)])

    def test_artifacts_attributes(self):
        logic.create_artifact_record(uuid='bandit_loot',
                                     level=1,
                                     utg_name=game_names.generator().get_test_name('artifact'),
                                     description='bandit loot description',
                                     type=relations.ARTIFACT_TYPE.HELMET,
                                     power_type=relations.ARTIFACT_POWER_TYPE.NEUTRAL)

        loot = objects.Artifact(record_id=storage.artifacts.get_by_uuid('bandit_loot').id, level=1)

        self.assertFalse(loot.is_useless)

    def test_artifacts(self):
        self.assertEqual(set(a.uuid for a in storage.artifacts.artifacts),
                         set(['helmet_1', 'plate_1', 'boots_1'] + heroes_relations.EQUIPMENT_SLOT.default_uids()))

    def test_loot(self):
        self.assertEqual(set(a.uuid for a in storage.artifacts.loot), set(['loot_1', 'loot_2', 'loot_3']))

    def test_artifacts_for_type(self):
        self.assertEqual(set([a.uuid for a in storage.artifacts.artifacts_for_type([relations.ARTIFACT_TYPE.HELMET,
                                                                                    relations.ARTIFACT_TYPE.BOOTS])]), set(['helmet_1', 'boots_1', 'default_boots']))
        self.assertEqual(set([a.uuid for a in storage.artifacts.artifacts_for_type([relations.ARTIFACT_TYPE.PLATE])]), set(['plate_1', 'default_plate']))

    def test_generate_artifact_from_list(self):

        helmet_2 = logic.create_random_artifact_record('helmet_2', type=relations.ARTIFACT_TYPE.HELMET)
        plate_2 = logic.create_random_artifact_record('plate_2', type=relations.ARTIFACT_TYPE.PLATE)
        boots_2 = logic.create_random_artifact_record('boots_2', type=relations.ARTIFACT_TYPE.BOOTS)

        helmet_3 = logic.create_random_artifact_record('helmet_3', type=relations.ARTIFACT_TYPE.HELMET)
        plate_3 = logic.create_random_artifact_record('plate_3', type=relations.ARTIFACT_TYPE.PLATE)
        boots_3 = logic.create_random_artifact_record('boots_3', type=relations.ARTIFACT_TYPE.BOOTS)

        artifacts = [helmet_2, plate_2, boots_2]
        artifacts_ids = [artifact.uuid for artifact in artifacts]
        for i in range(100):
            artifact = storage.artifacts.generate_artifact_from_list(artifacts, 1, rarity=relations.RARITY.NORMAL)
            self.assertTrue(artifact.id in artifacts_ids + heroes_relations.EQUIPMENT_SLOT.default_uids())

        artifacts = [helmet_3, plate_3, boots_3]
        artifacts_ids = [artifact.uuid for artifact in artifacts]
        for i in range(100):
            artifact = storage.artifacts.generate_artifact_from_list(artifacts, 1, rarity=relations.RARITY.NORMAL)
            self.assertTrue(artifact.id in artifacts_ids + heroes_relations.EQUIPMENT_SLOT.default_uids())

    def test_generate_artifact(self):
        self.hero.level = 5

        mob_record = mobs_logic.create_random_mob_record(uuid='bandit', level=2, state=mobs_relations.MOB_RECORD_STATE.ENABLED)
        mob = mobs_objects.Mob(record_id=mob_record.id, level=3)
        artifact_1 = logic.create_random_artifact_record('bandit_loot', mob=mob_record, type=relations.ARTIFACT_TYPE.USELESS, state=relations.ARTIFACT_RECORD_STATE.ENABLED)
        artifact_2 = logic.create_random_artifact_record('bandit_artifact', mob=mob_record, type=relations.ARTIFACT_TYPE.HELMET, state=relations.ARTIFACT_RECORD_STATE.ENABLED)

        with mock.patch('the_tale.game.heroes.objects.Hero.artifacts_probability', lambda self, mob: 1.0):
            with mock.patch('the_tale.game.heroes.objects.Hero.loot_probability', lambda self, mob: 1.0):
                artifact = storage.artifacts.generate_loot(self.hero, mob)

        self.assertEqual(artifact.level, mob.level)
        self.assertFalse(artifact.type.is_USELESS)
        self.assertEqual(artifact_2.id, artifact.record.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.artifacts_probability', lambda self, mob: 0.0):
            with mock.patch('the_tale.game.heroes.objects.Hero.loot_probability', lambda self, mob: 1.0):
                artifact = storage.artifacts.generate_loot(self.hero, mob)
        self.assertEqual(artifact.level, mob.record.level)
        self.assertTrue(artifact.type.is_USELESS)
        self.assertEqual(artifact_1.id, artifact.record.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.artifacts_probability', lambda self, mob: 0.0):
            with mock.patch('the_tale.game.heroes.objects.Hero.loot_probability', lambda self, mob: 0.0):
                self.assertEqual(storage.artifacts.generate_loot(self.hero, mob), None)

    @mock.patch('the_tale.game.heroes.objects.Hero.artifacts_probability', lambda self, mob: 1.0)
    def test_generate_artifact__rarity(self):
        self.hero.level = 5

        mob_record = mobs_logic.create_random_mob_record(uuid='bandit', level=2, state=mobs_relations.MOB_RECORD_STATE.ENABLED)
        mob = mobs_objects.Mob(record_id=mob_record.id, level=3)
        logic.create_random_artifact_record('bandit_artifact', mob=mob_record, type=relations.ARTIFACT_TYPE.HELMET, state=relations.ARTIFACT_RECORD_STATE.ENABLED)

        with mock.patch('the_tale.game.artifacts.storage.ArtifactsStorage.get_rarity_type', lambda self, hero: relations.RARITY.NORMAL):
            artifact = storage.artifacts.generate_loot(self.hero, mob)
            self.assertTrue(artifact.rarity.is_NORMAL)

        with mock.patch('the_tale.game.artifacts.storage.ArtifactsStorage.get_rarity_type', lambda self, hero: relations.RARITY.RARE):
            artifact = storage.artifacts.generate_loot(self.hero, mob)
            self.assertTrue(artifact.rarity.is_RARE)

        with mock.patch('the_tale.game.artifacts.storage.ArtifactsStorage.get_rarity_type', lambda self, hero: relations.RARITY.EPIC):
            artifact = storage.artifacts.generate_loot(self.hero, mob)
            self.assertTrue(artifact.rarity.is_EPIC)

    @mock.patch('the_tale.game.heroes.objects.Hero.artifacts_probability', lambda self, mob: 1.0)
    def test_generate_artifact__rarity_with_normal_probabilities(self):
        self.hero.level = 5

        mob_record = mobs_logic.create_random_mob_record(uuid='bandit', level=2, state=mobs_relations.MOB_RECORD_STATE.ENABLED)
        mob = mobs_objects.Mob(record_id=mob_record.id, level=3)
        logic.create_random_artifact_record('bandit_artifact', mob=mob_record, type=relations.ARTIFACT_TYPE.HELMET, state=relations.ARTIFACT_RECORD_STATE.ENABLED)

        rarities = set()

        for i in range(10000):
            artifact = storage.artifacts.generate_loot(self.hero, mob)
            rarities.add(artifact.rarity)

        self.assertEqual(rarities, set(relations.RARITY.records))

    @mock.patch('the_tale.game.artifacts.relations.RARITY.NORMAL.probability', 1)
    @mock.patch('the_tale.game.artifacts.relations.RARITY.RARE.probability', 0)
    @mock.patch('the_tale.game.artifacts.relations.RARITY.EPIC.probability', 0)
    def test_get_rarity_type__normal(self):
        self.assertTrue(storage.artifacts.get_rarity_type(self.hero))

    @mock.patch('the_tale.game.artifacts.relations.RARITY.NORMAL.probability', 0)
    @mock.patch('the_tale.game.artifacts.relations.RARITY.RARE.probability', 1)
    @mock.patch('the_tale.game.artifacts.relations.RARITY.EPIC.probability', 0)
    def test_get_rarity_type__rare(self):
        self.assertTrue(storage.artifacts.get_rarity_type(self.hero))

    @mock.patch('the_tale.game.artifacts.relations.RARITY.NORMAL.probability', 0)
    @mock.patch('the_tale.game.artifacts.relations.RARITY.RARE.probability', 0)
    @mock.patch('the_tale.game.artifacts.relations.RARITY.EPIC.probability', 1)
    def test_get_rarity_type__epic(self):
        self.assertTrue(storage.artifacts.get_rarity_type(self.hero))

    def test_disabled_artifacts(self):
        loot = logic.create_random_artifact_record('disabled_loot', type=relations.ARTIFACT_TYPE.USELESS, state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        artifact = logic.create_random_artifact_record('disabled_artifact', type=relations.ARTIFACT_TYPE.HELMET, state=relations.ARTIFACT_RECORD_STATE.DISABLED)

        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(a.uuid for a in storage.artifacts.artifacts))
        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(a.uuid for a in storage.artifacts.loot))
        self.assertFalse(set(['disabled_loot', 'disabled_artifact']) & set(storage.artifacts.artifacts_for_type([relations.ARTIFACT_TYPE.USELESS, relations.ARTIFACT_TYPE.HELMET])))

        self.assertEqual(storage.artifacts.generate_artifact_from_list([loot, artifact], level=1, rarity=relations.RARITY.NORMAL), None)

    def get_form_data(self, artifact):
        data = linguistics_helpers.get_word_post_data(artifact.utg_name, prefix='name')

        data.update({
            'level': str(artifact.level),
            'type': artifact.type,
            'power_type': artifact.power_type,
            'rare_effect': artifact.rare_effect,
            'epic_effect': artifact.epic_effect,
            'special_effect': artifact.special_effect,
            'description': artifact.description,
            'weapon_type': artifact.weapon_type,
            'material': artifact.material,
            'uuid': artifact.uuid,
            'mob': str(artifact.mob.id) if artifact.mob else ''})

        return data

    def test_change_uuid(self):
        loot = logic.create_random_artifact_record('some_loot', type=relations.ARTIFACT_TYPE.USELESS, state=relations.ARTIFACT_RECORD_STATE.DISABLED)

        form = forms.ModerateArtifactRecordForm(self.get_form_data(loot))

        self.assertTrue(form.is_valid())
        self.assertEqual(loot.uuid, storage.artifacts.get_by_uuid(loot.uuid).uuid)

        logic.update_by_moderator(loot, form)

        self.assertEqual(loot.uuid, storage.artifacts.get_by_uuid(loot.uuid).uuid)

    def test_disable_default_equipment(self):
        artifact_uid = random.choice(heroes_relations.EQUIPMENT_SLOT.default_uids())

        data = self.get_form_data(storage.artifacts.get_by_uuid(artifact_uid))
        data['approved'] = False

        form = forms.ModerateArtifactRecordForm(data)
        self.assertTrue(form.is_valid())

        default_artifact = storage.artifacts.get_by_uuid(artifact_uid)

        self.assertRaises(exceptions.DisableDefaultEquipmentError, logic.update_by_moderator, default_artifact, form)

    def test_preference_rating(self):
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 100), power.PowerDistribution(0.5, 0.5)), 100)
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 100), power.PowerDistribution(0.2, 0.8)), 100)
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 100), power.PowerDistribution(0.8, 0.2)), 100)

        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 200), power.PowerDistribution(0.5, 0.5)), 150)
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 200), power.PowerDistribution(0.2, 0.8)), 180)
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 200), power.PowerDistribution(0.8, 0.2)), 120)

        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(200, 100), power.PowerDistribution(0.5, 0.5)), 150)
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(200, 100), power.PowerDistribution(0.2, 0.8)), 120)
        self.assertEqual(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(200, 100), power.PowerDistribution(0.8, 0.2)), 180)

    def test_preference_rating__rarity(self):
        self.assertTrue(objects.Artifact._preference_rating(relations.RARITY.NORMAL, power.Power(100, 100), power.PowerDistribution(0.5, 0.5)) <
                        objects.Artifact._preference_rating(relations.RARITY.RARE, power.Power(100, 100), power.PowerDistribution(0.5, 0.5)) <
                        objects.Artifact._preference_rating(relations.RARITY.EPIC, power.Power(100, 100), power.PowerDistribution(0.5, 0.5)))

    def test_make_better_than__already_better(self):
        artifact_1 = self.artifact_record.create_artifact(level=1, power=power.Power(2, 2))
        artifact_2 = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))

        old_power = artifact_1.power.clone()

        artifact_1.make_better_than(artifact_2, power.PowerDistribution(0.5, 0.5))

        self.assertEqual(artifact_1.power, old_power)

    def test_make_better_than__physic(self):
        artifact_1 = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact_2 = self.artifact_record.create_artifact(level=1, power=power.Power(3, 3))

        artifact_1.make_better_than(artifact_2, power.PowerDistribution(1.0, 0))

        self.assertEqual(artifact_1.power.magic, 1)
        self.assertTrue(artifact_1.power.physic > 3)

    def test_make_better_than__magic(self):
        artifact_1 = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact_2 = self.artifact_record.create_artifact(level=1, power=power.Power(3, 3))

        artifact_1.make_better_than(artifact_2, power.PowerDistribution(0, 1.0))

        self.assertTrue(artifact_1.power.magic > 3)
        self.assertEqual(artifact_1.power.physic, 1)

    def test_make_better_than__both(self):
        artifact_1 = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact_2 = self.artifact_record.create_artifact(level=1, power=power.Power(100, 100))

        artifact_1.make_better_than(artifact_2, power.PowerDistribution(0.5, 0.5))

        self.assertTrue(artifact_1.power.physic > 100 or artifact_1.power.magic > 100)

    def test_sharp__no_choices(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))

        old_integrity = artifact.integrity
        old_max_integrity = artifact.max_integrity

        artifact.sharp(distribution=power.PowerDistribution(0.5, 0.5), max_power=power.Power(1, 1))

        self.assertEqual(artifact.power, power.Power(1, 1))
        self.assertEqual(old_integrity, artifact.integrity)
        self.assertEqual(old_max_integrity, artifact.max_integrity)

    def test_sharp__integrity_lost(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))

        old_integrity = artifact.integrity
        old_max_integrity = artifact.max_integrity

        artifact.sharp(distribution=power.PowerDistribution(0.5, 0.5), max_power=power.Power(3, 3))

        self.assertTrue(old_integrity > artifact.integrity)
        self.assertTrue(old_max_integrity > artifact.max_integrity)
        self.assertEqual(artifact.integrity, artifact.max_integrity)

        artifact.integrity /= 2
        old_integrity = artifact.integrity
        old_max_integrity = artifact.max_integrity

        artifact.sharp(distribution=power.PowerDistribution(0.5, 0.5), max_power=power.Power(3, 3))

        self.assertEqual(old_integrity, artifact.integrity)
        self.assertTrue(old_max_integrity > artifact.max_integrity)

    def test_sharp__physic(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.sharp(distribution=power.PowerDistribution(1.0, 0.0), max_power=power.Power(3, 3))
        artifact.sharp(distribution=power.PowerDistribution(1.0, 0.0), max_power=power.Power(3, 3))
        self.assertEqual(artifact.power, power.Power(3, 1))

    def test_sharp__magic(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.sharp(distribution=power.PowerDistribution(0.0, 1.0), max_power=power.Power(3, 3))
        artifact.sharp(distribution=power.PowerDistribution(0.0, 1.0), max_power=power.Power(3, 3))
        self.assertEqual(artifact.power, power.Power(1, 3))

    def test_sharp__both(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.sharp(distribution=power.PowerDistribution(0.5, 0.5), max_power=power.Power(2, 2))
        artifact.sharp(distribution=power.PowerDistribution(0.5, 0.5), max_power=power.Power(2, 2))
        self.assertEqual(artifact.power, power.Power(2, 2))

    def test_sharp__no_choices__and_force(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.sharp(distribution=power.PowerDistribution(0.5, 0.5), max_power=power.Power(1, 1), force=True)
        self.assertEqual(artifact.power.total(), 3)

    def test_can_be_broken__barrier(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        self.assertFalse(artifact.can_be_broken())

    def test_can_be_broken(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.integrity = int(artifact.max_integrity * (1 - c.ARTIFACT_INTEGRITY_SAFE_BARRIER)) - 1
        self.assertTrue(artifact.can_be_broken())

    def test_break_it(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(100, 100))
        artifact.integrity = artifact.max_integrity / 2

        old_integrity = artifact.integrity
        old_max_integrity = artifact.max_integrity

        artifact.break_it()

        self.assertTrue(artifact.power.magic < 100)
        self.assertTrue(artifact.power.physic < 100)
        self.assertTrue(old_max_integrity > artifact.max_integrity)
        self.assertEqual(old_integrity, artifact.integrity)

    def test_break_it__zero(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.integrity = artifact.max_integrity / 2

        old_integrity = artifact.integrity
        old_max_integrity = artifact.max_integrity

        artifact.break_it()

        self.assertEqual(artifact.power, power.Power(1, 1))
        self.assertTrue(old_max_integrity > artifact.max_integrity)
        self.assertEqual(old_integrity, artifact.integrity)

    def test_break_it__large_integrity(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))

        old_max_integrity = artifact.max_integrity

        artifact.break_it()

        self.assertEqual(artifact.power, power.Power(1, 1))
        self.assertTrue(old_max_integrity > artifact.max_integrity)
        self.assertEqual(artifact.integrity, artifact.max_integrity)

    def test_repair_it(self):
        artifact = self.artifact_record.create_artifact(level=1, power=power.Power(1, 1))
        artifact.integrity = artifact.max_integrity - 1
        artifact.repair_it()
        self.assertEqual(artifact.integrity, artifact.max_integrity)


class WeaponTests(utils_testcase.TestCase):

    def setUp(self):
        super(WeaponTests, self).setUp()
        game_logic.create_test_map()

        self.weapon = objects.Weapon(weapon=relations.STANDARD_WEAPON.WEAPON_5,
                                     material=tt_artifacts_relations.MATERIAL.MATERIAL_2,
                                     power_type=relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL)

    def test_init(self):
        self.assertTrue(self.weapon.type.is_WEAPON_5)
        self.assertTrue(self.weapon.material.is_MATERIAL_2)
        self.assertTrue(self.weapon.power_type.is_MOST_PHYSICAL)

        self.assertEqual(self.weapon._restrictions,
                         [linguistics_restrictions.get(relations.ARTIFACT_TYPE.MAIN_HAND),
                          linguistics_restrictions.get(relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL),
                          linguistics_restrictions.get(relations.RARITY.NORMAL),
                          linguistics_restrictions.get(relations.ARTIFACT_EFFECT.NO_EFFECT),
                          linguistics_restrictions.get(tt_artifacts_relations.WEAPON_TYPE.TYPE_3),
                          linguistics_restrictions.get(tt_artifacts_relations.MATERIAL.MATERIAL_2),

                          linguistics_restrictions.get(tt_artifacts_relations.DAMAGE_TYPE.TYPE_2),
                          linguistics_restrictions.get(tt_artifacts_relations.DAMAGE_TYPE.TYPE_5)])

    def test_serialization(self):
        self.assertEqual(self.weapon, objects.Weapon.deserialize(self.weapon.serialize()))
