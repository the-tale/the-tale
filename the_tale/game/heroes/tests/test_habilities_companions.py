# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions.abilities import relations as companions_abilities_relations

from the_tale.game.heroes.habilities import companions
from the_tale.game.heroes.relations import MODIFIERS


class HabilitiesCompanionsTest(testcase.TestCase):

    def setUp(self):
        super(HabilitiesCompanionsTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]


    def test_walker(self):
        self.assertEqual(companions.WALKER().modify_attribute(MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                        {companions_abilities_relations.METATYPE.TRAVEL: 1})
        self.assertEqual(companions.WALKER().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(companions.WALKER.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.TRAVEL: 3})

    def test_comrade(self):
        self.assertEqual(companions.COMRADE().modify_attribute(MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                        {companions_abilities_relations.METATYPE.BATTLE: 1})
        self.assertEqual(companions.COMRADE().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(companions.COMRADE.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.BATTLE: 3})

    def test_improviser(self):
        self.assertEqual(companions.IMPROVISER().modify_attribute(MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                        {companions_abilities_relations.METATYPE.OTHER: 1})
        self.assertEqual(companions.IMPROVISER().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(companions.IMPROVISER.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.OTHER: 3})

    def test_economic(self):
        self.assertEqual(companions.ECONOMIC().modify_attribute(MODIFIERS.COMPANION_ABILITIES_LEVELS, {}),
                        {companions_abilities_relations.METATYPE.MONEY: 1})
        self.assertEqual(companions.ECONOMIC().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_ABILITIES_LEVELS,)), {}), {})

        self.assertEqual(self.hero.companion_abilities_levels, {})
        self.hero.abilities.add(companions.ECONOMIC.get_id(), 3)
        self.assertEqual(self.hero.companion_abilities_levels, {companions_abilities_relations.METATYPE.MONEY: 3})

    def test_thoughtful(self):
        self.assertEqual(companions.THOUGHTFUL().modify_attribute(MODIFIERS.COMPANION_MAX_HEALTH, 1.0), 1.1)
        self.assertEqual(companions.THOUGHTFUL().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_MAX_HEALTH,)), 1), 1)

        self.assertEqual(self.hero.companion_max_health_multiplier, 1)
        self.hero.abilities.add(companions.THOUGHTFUL.get_id(), 3)
        self.assertEqual(self.hero.companion_max_health_multiplier, 1.3)

    def test_coherence(self):
        self.assertEqual(companions.COHERENCE().modify_attribute(MODIFIERS.COMPANION_MAX_COHERENCE, 0), 20)
        self.assertEqual(companions.COHERENCE().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_MAX_COHERENCE,)), 1), 1)

        self.assertEqual(self.hero.companion_max_coherence, 20) # coherence lvl 1 — default hero ability
        self.hero.abilities.add(companions.COHERENCE.get_id(), 3)
        self.assertEqual(self.hero.companion_max_coherence, 60)

    def test_healing(self):
        self.assertEqual(companions.HEALING().modify_attribute(MODIFIERS.COMPANION_LIVING_HEAL, 0), 0.01)
        self.assertEqual(companions.HEALING().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_LIVING_HEAL,)), 0), 0)

        self.assertEqual(self.hero.companion_living_heal_probability, 0)
        self.hero.abilities.add(companions.HEALING.get_id(), 3)
        self.assertEqual(self.hero.companion_living_heal_probability, 0.03)

    def test_mage_mechanincs(self):
        self.assertEqual(companions.MAGE_MECHANICS().modify_attribute(MODIFIERS.COMPANION_CONSTRUCT_HEAL, 0), 0.01)
        self.assertEqual(companions.MAGE_MECHANICS().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_CONSTRUCT_HEAL,)), 0), 0)

        self.assertEqual(self.hero.companion_construct_heal_probability, 0)
        self.hero.abilities.add(companions.MAGE_MECHANICS.get_id(), 3)
        self.assertEqual(self.hero.companion_construct_heal_probability, 0.03)

    def test_witchcraft(self):
        self.assertEqual(companions.WITCHCRAFT().modify_attribute(MODIFIERS.COMPANION_UNUSUAL_HEAL, 0), 0.01)
        self.assertEqual(companions.WITCHCRAFT().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_UNUSUAL_HEAL,)), 0), 0)

        self.assertEqual(self.hero.companion_unusual_heal_probability, 0)
        self.hero.abilities.add(companions.WITCHCRAFT.get_id(), 3)
        self.assertEqual(self.hero.companion_unusual_heal_probability, 0.03)

    def test_sociability(self):
        self.assertEqual(companions.SOCIABILITY().modify_attribute(MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED, 1), 1.2)
        self.assertEqual(companions.SOCIABILITY().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED,)), 1), 1)

        self.assertEqual(self.hero.companion_living_coherence_speed, 1)
        self.hero.abilities.add(companions.SOCIABILITY.get_id(), 3)
        self.assertEqual(self.hero.companion_living_coherence_speed, 1.6)

    def test_service(self):
        self.assertEqual(companions.SERVICE().modify_attribute(MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED, 1), 1.2)
        self.assertEqual(companions.SERVICE().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED,)), 1), 1)

        self.assertEqual(self.hero.companion_construct_coherence_speed, 1)
        self.hero.abilities.add(companions.SERVICE.get_id(), 3)
        self.assertEqual(self.hero.companion_construct_coherence_speed, 1.6)

    def test_sacredness(self):
        self.assertEqual(companions.SACREDNESS().modify_attribute(MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED, 1), 1.2)
        self.assertEqual(companions.SACREDNESS().modify_attribute(MODIFIERS.random(exclude=(MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED,)), 1), 1)

        self.assertEqual(self.hero.companion_unusual_coherence_speed, 1)
        self.hero.abilities.add(companions.SACREDNESS.get_id(), 3)
        self.assertEqual(self.hero.companion_unusual_coherence_speed, 1.6)
