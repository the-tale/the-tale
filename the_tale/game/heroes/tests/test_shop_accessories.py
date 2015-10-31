# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.balance.power import Power
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.artifacts.prototypes import ArtifactPrototype
from the_tale.game.artifacts.relations import RARITY

from the_tale.game.heroes.conf import heroes_settings


class ShopAccessoriesTest(testcase.TestCase):

    def setUp(self):
        super(ShopAccessoriesTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    def test_purchase_energy_bonus(self):
        self.assertEqual(self.hero.energy_bonus, heroes_settings.START_ENERGY_BONUS)
        self.hero.purchase_energy_bonus(100)
        self.assertEqual(self.hero.energy_bonus, 100 + heroes_settings.START_ENERGY_BONUS)

    def test_purchase_reset_abilities(self):
        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.reset') as reset:
            self.hero.purchase_reset_abilities()

        self.assertEqual(reset.call_count, 1)

    def test_purchase_rechooce_abilities_choice(self):
        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.rechooce_choices') as rechooce_choices:
            self.hero.purchase_rechooce_abilities_choices()

        self.assertEqual(rechooce_choices.call_count, 1)

    @mock.patch('the_tale.game.heroes.objects.Hero.experience_modifier', 1.0)
    def test_purchase_experience(self):
        self.assertEqual(self.hero.experience, 0)
        self.hero.purchase_experience(1)
        self.assertEqual(self.hero.experience, 1)

    def test_purchase_artifact__normal(self):
        with self.check_delta(lambda: self.hero.bag.occupation, 1):
            artifact = self.hero.purchase_artifact(rarity=RARITY.NORMAL, better=False)

        self.assertTrue(artifact.rarity.is_NORMAL)
        self.assertEqual(artifact, self.hero.bag.values()[0])

    def test_purchase_artifact__rare(self):
        with self.check_delta(lambda: self.hero.bag.occupation, 1):
            artifact = self.hero.purchase_artifact(rarity=RARITY.RARE, better=False)

        self.assertTrue(artifact.rarity.is_RARE)
        self.assertEqual(artifact, self.hero.bag.values()[0])

    def test_purchase_artifact__epic(self):
        with self.check_delta(lambda: self.hero.bag.occupation, 1):
            artifact = self.hero.purchase_artifact(rarity=RARITY.EPIC, better=False)

        self.assertTrue(artifact.rarity.is_EPIC)
        self.assertEqual(artifact, self.hero.bag.values()[0])

    def test_purchase_artifact__full_bag(self):
        self.assertEqual(self.hero.bag.occupation, 0)

        for i in xrange(self.hero.max_bag_size*2):
            self.hero.purchase_artifact(rarity=RARITY.NORMAL, better=True)

        self.assertEqual(self.hero.bag.occupation, self.hero.max_bag_size*2)

    def test_purchase_artifact__better_artifact__min_level(self):
        self.assertEqual(self.hero.level, 1)

        rarity = RARITY.NORMAL
        distribution = self.hero.preferences.archetype.power_distribution
        middle_power = Power.power_to_artifact(distribution, self.hero.level)

        for i in xrange(100):
            self.assertTrue(self.hero.purchase_artifact(rarity=RARITY.NORMAL, better=True).preference_rating(distribution) >
                            ArtifactPrototype._preference_rating(rarity, middle_power, distribution))


    def test_purchase_artifact__better_artifact__large_level(self):
        self.hero.level = 100

        self.assertEqual(self.hero.level, 100)

        rarity = RARITY.NORMAL
        distribution = self.hero.preferences.archetype.power_distribution
        middle_power = Power.power_to_artifact(distribution, self.hero.level)

        N = 100

        with mock.patch('the_tale.game.actions.container.ActionsContainer.request_replane') as request_replane:
            for i in xrange(N):
                self.assertTrue(self.hero.purchase_artifact(rarity=RARITY.NORMAL, better=True).preference_rating(distribution) >
                                ArtifactPrototype._preference_rating(rarity, middle_power, distribution))

        self.assertEqual(request_replane.call_count, N)


    def test_purchase_artifact__not_better_artifact__large_level(self):
        self.hero.level = 100

        self.assertEqual(self.hero.level, 100)

        rarity = RARITY.NORMAL
        distribution = self.hero.preferences.archetype.power_distribution
        middle_power = Power.power_to_artifact(distribution, self.hero.level)

        N = 100

        results = set()

        with mock.patch('the_tale.game.actions.container.ActionsContainer.request_replane') as request_replane:
            for i in xrange(N):
                results.add(self.hero.purchase_artifact(rarity=RARITY.NORMAL, better=False).preference_rating(distribution) >
                            ArtifactPrototype._preference_rating(rarity, middle_power, distribution))

        self.assertEqual(results, set([True, False]))
        self.assertEqual(request_replane.call_count, N)


    def test_purchase_card(self):
        from the_tale.game.cards.relations import CARD_TYPE

        self.assertFalse(self.hero.cards.has_cards)

        self.hero.purchase_card(CARD_TYPE.KEEPERS_GOODS_COMMON, count=3)

        self.assertEqual(self.hero.cards.cards_count(), 3)
        self.assertEqual([card.type for card in self.hero.cards.all_cards()], [CARD_TYPE.KEEPERS_GOODS_COMMON]*3)
