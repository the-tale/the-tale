
import smart_imports

smart_imports.all()


class AttributeAbiliesForHeroTest(utils_testcase.TestCase):

    def setUp(self):
        super(AttributeAbiliesForHeroTest, self).setUp()
        game_logic.create_test_map()

        account = self.accounts_factory.create_account()
        self.hero = logic.load_hero(account_id=account.id)

    def tearDown(self):
        pass

    def test_extra_slow(self):
        self.assertTrue(heroes_abilities_attributes.EXTRA_SLOW().availability.is_FOR_MONSTERS)

    def test_slow(self):
        self.assertTrue(heroes_abilities_attributes.SLOW().availability.is_FOR_MONSTERS)

    def test_fast(self):
        self.assertTrue(heroes_abilities_attributes.FAST().availability.is_FOR_ALL)

        old_initiative = self.hero.initiative

        self.hero.abilities.add(heroes_abilities_attributes.FAST.get_id())

        self.assertTrue(old_initiative < self.hero.initiative)

    def test_extra_fast(self):
        self.assertTrue(heroes_abilities_attributes.EXTRA_FAST().availability.is_FOR_MONSTERS)

    def test_extra_thin(self):
        self.assertTrue(heroes_abilities_attributes.EXTRA_THIN().availability.is_FOR_MONSTERS)

    def test_thin(self):
        self.assertTrue(heroes_abilities_attributes.THIN().availability.is_FOR_MONSTERS)

    def test_thick(self):
        self.assertTrue(heroes_abilities_attributes.THICK().availability.is_FOR_ALL)

        old_max_health = self.hero.max_health

        self.hero.abilities.add(heroes_abilities_attributes.THICK.get_id())

        self.assertTrue(old_max_health < self.hero.max_health)

    def test_extra_thick(self):
        self.assertTrue(heroes_abilities_attributes.EXTRA_THICK().availability.is_FOR_MONSTERS)

    def test_extra_weak(self):
        self.assertTrue(heroes_abilities_attributes.EXTRA_WEAK().availability.is_FOR_MONSTERS)

    def test_weak(self):
        self.assertTrue(heroes_abilities_attributes.WEAK().availability.is_FOR_MONSTERS)

    def test_strong(self):
        self.assertTrue(heroes_abilities_attributes.STRONG().availability.is_FOR_ALL)

        old_damage_modifier = self.hero.damage_modifier

        self.hero.abilities.add(heroes_abilities_attributes.STRONG.get_id())

        self.assertTrue(old_damage_modifier < self.hero.damage_modifier)

    def test_extra_strong(self):
        self.assertTrue(heroes_abilities_attributes.EXTRA_STRONG().availability.is_FOR_MONSTERS)


class AttributeAbiliesForMobTest(utils_testcase.TestCase):

    def setUp(self):
        super(AttributeAbiliesForMobTest, self).setUp()

        game_logic.create_test_map()

        self.mob1 = self.construct_mob_with_abilities(abilities=[heroes_abilities_attributes.EXTRA_SLOW.get_id(), heroes_abilities_attributes.EXTRA_THIN.get_id(), heroes_abilities_attributes.EXTRA_WEAK.get_id()], index=1)
        self.mob2 = self.construct_mob_with_abilities(abilities=[heroes_abilities_attributes.SLOW.get_id(), heroes_abilities_attributes.THIN.get_id(), heroes_abilities_attributes.WEAK.get_id()], index=2)
        self.mob3 = self.construct_mob_with_abilities(abilities=[heroes_abilities_attributes.FAST.get_id(), heroes_abilities_attributes.THICK.get_id(), heroes_abilities_attributes.STRONG.get_id()], index=3)
        self.mob4 = self.construct_mob_with_abilities(abilities=[heroes_abilities_attributes.EXTRA_FAST.get_id(), heroes_abilities_attributes.EXTRA_THICK.get_id(), heroes_abilities_attributes.EXTRA_STRONG.get_id()], index=4)

    @staticmethod
    def construct_mob_with_abilities(abilities, index):
        uuid = 'test_mob %d' % index
        mob_record = mobs_logic.create_random_mob_record(uuid,
                                                         level=1,
                                                         utg_name=game_names.generator().get_test_name(uuid),
                                                         description='',
                                                         abilities=abilities,
                                                         terrains=[],
                                                         type=tt_beings_relations.TYPE.CIVILIZED,
                                                         state=mobs_relations.MOB_RECORD_STATE.ENABLED)
        return mobs_objects.Mob(level=1, record_id=mob_record.id)

    def tearDown(self):
        pass

    def test_slow_fast(self):
        self.assertTrue(self.mob1.initiative < self.mob2.initiative < self.mob3.initiative < self.mob4.initiative)

    def test_thin_thick(self):
        self.assertTrue(self.mob1.max_health < self.mob2.max_health < self.mob3.max_health < self.mob4.max_health)

    def test_weak_strong(self):
        self.assertTrue(self.mob1.damage_modifier < self.mob2.damage_modifier < self.mob3.damage_modifier < self.mob4.damage_modifier)
