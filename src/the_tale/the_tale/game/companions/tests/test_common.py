
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage
from the_tale.game import turn

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions import logic
from the_tale.game.companions import relations

from the_tale.game.companions.tests import helpers


class CommonTests(testcase.TestCase):

    def setUp(self):
        super(CommonTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]


    def test_rarities_abilities(self):
        for rarity, rarity_abilities in helpers.RARITIES_ABILITIES.items():
            companion = logic.create_random_companion_record('%s companion' % rarity,
                                                             abilities=rarity_abilities)
            self.assertEqual(companion.rarity, rarity)


    @mock.patch('the_tale.game.companions.objects.Companion.max_coherence', 100)
    @mock.patch('the_tale.game.heroes.habilities.companions.THOUGHTFUL.MULTIPLIER', [1, 1, 1, 1, 1])
    @mock.patch('the_tale.game.heroes.habilities.companions._CompanionHealBase.PROBABILITY', [0, 0, 0, 0, 0])
    def _test_companion_death_speed(self):
        companion_record = logic.create_random_companion_record('test companion',
                                                                state=relations.STATE.ENABLED,
                                                                dedication=relations.DEDICATION.BRAVE)#,#,;
        companion = logic.create_companion(companion_record)
        self.hero.set_companion(companion)
        self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.NORMAL)

        old_health = self.hero.companion.health

        while self.hero.companion:
            self.hero.companion.coherence = 50

            self.storage.process_turn()
            turn.increment()

            self.hero.randomized_level_up()

            if not self.hero.is_alive:
                if hasattr(self.hero.actions.current_action, 'fast_resurrect'):
                    self.hero.actions.current_action.fast_resurrect()

            if self.hero.companion:
                old_health = self.hero.companion.health
