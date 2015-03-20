# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage
from the_tale.game import prototypes as game_prototypes

from the_tale.game.balance import constants as c

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions import logic
from the_tale.game.companions import relations

from the_tale.game.companions.abilities import container as abilities_container
from the_tale.game.companions.abilities import effects

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
        for rarity, rarity_abilities in helpers.RARITIES_ABILITIES.iteritems():
            companion = logic.create_random_companion_record('%s companion' % rarity,
                                                             abilities=rarity_abilities)
            self.assertEqual(companion.rarity, rarity)


    @mock.patch('the_tale.game.companions.objects.Companion.max_coherence', 100)
    @mock.patch('the_tale.game.heroes.habilities.companions.THOUGHTFUL.MULTIPLIER', [1, 1, 1, 1, 1])
    @mock.patch('the_tale.game.heroes.habilities.companions._CompanionHealBase.PROBABILITY', [0, 0, 0, 0, 0])
    def _test_companion_death_speed(self):
        current_time = game_prototypes.TimePrototype.get_current_time()

        companion_record = logic.create_random_companion_record('test companion',
                                                                state=relations.STATE.ENABLED,
                                                                dedication=relations.DEDICATION.BRAVE)#,#,;
                                                                # abilities=abilities_container.Container(start=(effects.ABILITIES.BODYGUARD,)),# effects.ABILITIES.PUNY)),
                                                                # dedication=relations.DEDICATION.HEROIC)
                                                                # abilities=abilities_container.Container(common=(effects.ABILITIES.COWARDLY, )),
                                                                # dedication=relations.DEDICATION.INDECISIVE)
        companion = logic.create_companion(companion_record)
        self.hero.set_companion(companion)
        # self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.EGOISM)
        self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.NORMAL)
        # self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.ALTRUISM)
        # self.hero.preferences.set_companion_dedication(heroes_relations.COMPANION_DEDICATION.EVERY_MAN_FOR_HIMSELF)

        old_health = self.hero.companion.health

        print 'defend_probability: ', self.hero.companion.defend_in_battle_probability

        # for i in xrange(50):
        #     self.hero.randomized_level_up(increment_level=True)

        while self.hero.companion:
            self.hero.companion.coherence = 50

            self.storage.process_turn()
            current_time.increment_turn()

            self.hero.randomized_level_up()

            if not self.hero.is_alive:
                if hasattr(self.hero.actions.current_action, 'fast_resurrect'):
                    self.hero.actions.current_action.fast_resurrect()
                print '!'

            if self.hero.companion:
                if old_health != self.hero.companion.health:
                    print '%.2f:\t%s -> %s [%s] c%s' % ( (current_time.turn_number / c.TURNS_IN_HOUR / 24.0),
                                                          self.hero.companion.health - self.hero.companion.max_health,
                                                          self.hero.companion.health,
                                                          self.hero.companion.health - old_health,
                                                          self.hero.companion.coherence)

                old_health = self.hero.companion.health
