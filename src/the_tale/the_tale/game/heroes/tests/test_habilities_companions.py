
import smart_imports

smart_imports.all()


class HabilitiesCompanionsTest(utils_testcase.TestCase):

    def setUp(self):
        super(HabilitiesCompanionsTest, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def test_walker(self):
        self.assertEqual(heroes_abilities_companions.WALKER().modify_attribute(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                         {companions_abilities_relations.METATYPE.TRAVEL: 1})
        self.assertEqual(heroes_abilities_companions.WALKER().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(heroes_abilities_companions.WALKER.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.TRAVEL: 3})

    def test_comrade(self):
        self.assertEqual(heroes_abilities_companions.COMRADE().modify_attribute(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                         {companions_abilities_relations.METATYPE.BATTLE: 1})
        self.assertEqual(heroes_abilities_companions.COMRADE().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(heroes_abilities_companions.COMRADE.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.BATTLE: 3})

    def test_improviser(self):
        self.assertEqual(heroes_abilities_companions.IMPROVISER().modify_attribute(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                         {companions_abilities_relations.METATYPE.OTHER: 1})
        self.assertEqual(heroes_abilities_companions.IMPROVISER().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(heroes_abilities_companions.IMPROVISER.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.OTHER: 3})

    def test_economic(self):
        self.assertEqual(heroes_abilities_companions.ECONOMIC().modify_attribute(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                         {companions_abilities_relations.METATYPE.MONEY: 1})
        self.assertEqual(heroes_abilities_companions.ECONOMIC().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(heroes_abilities_companions.ECONOMIC.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.MONEY: 3})

    def test_thoughtful(self):
        self.assertEqual(heroes_abilities_companions.THOUGHTFUL().modify_attribute(relations.MODIFIERS.COMPANION_MAX_HEALTH, 1.0), 1.1)
        self.assertEqual(heroes_abilities_companions.THOUGHTFUL().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_MAX_HEALTH,)), 1), 1)

        self.assertEqual(self.hero.companion_max_health_multiplier, 1)
        self.hero.abilities.add(heroes_abilities_companions.THOUGHTFUL.get_id(), 3)
        self.assertEqual(self.hero.companion_max_health_multiplier, 1.3)

    def test_coherence(self):
        self.assertEqual(heroes_abilities_companions.COHERENCE().modify_attribute(relations.MODIFIERS.COMPANION_MAX_COHERENCE, 0), 20)
        self.assertEqual(heroes_abilities_companions.COHERENCE().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_MAX_COHERENCE,)), 1), 1)

        self.assertEqual(self.hero.companion_max_coherence, 20)  # coherence lvl 1 — default hero ability
        self.hero.abilities.add(heroes_abilities_companions.COHERENCE.get_id(), 3)
        self.assertEqual(self.hero.companion_max_coherence, 60)

    def test_healing(self):
        self.assertEqual(heroes_abilities_companions.HEALING().modify_attribute(relations.MODIFIERS.COMPANION_LIVING_HEAL, 0),
                         0.08680555555555557)
        self.assertEqual(heroes_abilities_companions.HEALING().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_LIVING_HEAL,)), 0), 0)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.type', tt_beings_relations.TYPE.ANIMAL):
            self.assertEqual(self.hero.companion_heal_probability, 0)
            self.hero.abilities.add(heroes_abilities_companions.HEALING.get_id(), 3)
            self.assertEqual(self.hero.companion_heal_probability, 0.2604166666666667)

    def test_mage_mechanincs(self):
        self.assertEqual(heroes_abilities_companions.MAGE_MECHANICS().modify_attribute(relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL, 0),
                         0.08680555555555557)
        self.assertEqual(heroes_abilities_companions.MAGE_MECHANICS().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL,)), 0), 0)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.type', tt_beings_relations.TYPE.MECHANICAL):
            self.assertEqual(self.hero.companion_heal_probability, 0)
            self.hero.abilities.add(heroes_abilities_companions.MAGE_MECHANICS.get_id(), 3)
            self.assertEqual(self.hero.companion_heal_probability, 0.2604166666666667)

    def test_witchcraft(self):
        self.assertEqual(heroes_abilities_companions.WITCHCRAFT().modify_attribute(relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, 0),
                         0.08680555555555557)
        self.assertEqual(heroes_abilities_companions.WITCHCRAFT().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_UNUSUAL_HEAL,)), 0), 0)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.type', tt_beings_relations.TYPE.SUPERNATURAL):
            self.assertEqual(self.hero.companion_heal_probability, 0)
            self.hero.abilities.add(heroes_abilities_companions.WITCHCRAFT.get_id(), 3)
            self.assertEqual(self.hero.companion_heal_probability, 0.2604166666666667)

    def test_sociability(self):
        self.assertEqual(heroes_abilities_companions.SOCIABILITY().modify_attribute(relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED, 1), 1.2)
        self.assertEqual(heroes_abilities_companions.SOCIABILITY().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED,)), 1), 1)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.type', tt_beings_relations.TYPE.ANIMAL):
            self.assertEqual(self.hero.companion_coherence_speed, 1)
            self.hero.abilities.add(heroes_abilities_companions.SOCIABILITY.get_id(), 3)
            self.assertEqual(self.hero.companion_coherence_speed, 1.6)

    def test_service(self):
        self.assertEqual(heroes_abilities_companions.SERVICE().modify_attribute(relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED, 1), 1.2)
        self.assertEqual(heroes_abilities_companions.SERVICE().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED,)), 1), 1)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.type', tt_beings_relations.TYPE.MECHANICAL):
            self.assertEqual(self.hero.companion_coherence_speed, 1)
            self.hero.abilities.add(heroes_abilities_companions.SERVICE.get_id(), 3)
            self.assertEqual(self.hero.companion_coherence_speed, 1.6)

    def test_sacredness(self):
        self.assertEqual(heroes_abilities_companions.SACREDNESS().modify_attribute(relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED, 1), 1.2)
        self.assertEqual(heroes_abilities_companions.SACREDNESS().modify_attribute(relations.MODIFIERS.random(exclude=(relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED,)), 1), 1)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.type', tt_beings_relations.TYPE.SUPERNATURAL):
            self.assertEqual(self.hero.companion_coherence_speed, 1)
            self.hero.abilities.add(heroes_abilities_companions.SACREDNESS.get_id(), 3)
            self.assertEqual(self.hero.companion_coherence_speed, 1.6)
