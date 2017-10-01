
import uuid
import random

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.cards.tests.helpers import CardsTestMixin

from .. import tt_api
from .. import effects


class FreezeCompanionTests(CardsTestMixin, testcase.TestCase):
    CARD = cards.CARD.FREEZE_COMPANION

    def setUp(self):
        super(FreezeCompanionTests, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        tt_api.debug_clear_service()

    def prepair_data(self, available_for_auction):

        card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=available_for_auction)

        self.assertEqual(tt_api.load_cards(self.account_1.id), {})

        old_companion_record = random.choice(companions_storage.companions.all())

        self.hero.set_companion(companions_logic.create_companion(old_companion_record))

        return card


    def check_freeze(self, expected_rarity):

        self.assertEqual(self.hero.companion, None)

        cards = tt_api.load_cards(self.account_1.id)

        self.assertEqual(len(cards), 1)

        card = list(cards.values())[0]

        self.assertEqual(card.effect.__class__, effects.GetCompanion)

        self.assertEqual(card.type.rarity, expected_rarity.card_rarity)


    def test_use__has_companion__available_for_auction(self):
        expected_rarity = companions_relations.RARITY.random()

        card = self.prepair_data(available_for_auction=True)

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.rarity', expected_rarity):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_freeze(expected_rarity)

        self.assertTrue(card.available_for_auction)


    def test_use__has_companion__not_available_for_auction(self):
        expected_rarity = companions_relations.RARITY.random()

        card = self.prepair_data(available_for_auction=False)

        with mock.patch('the_tale.game.companions.objects.CompanionRecord.rarity', expected_rarity):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_freeze(expected_rarity)

        self.assertFalse(card.available_for_auction)


    def test_use__has_companion__can_not_be_freezed(self):
        expected_rarity = companions_relations.RARITY.random()

        card = self.prepair_data(available_for_auction=False)

        with mock.patch('the_tale.game.companions.abilities.container.Container.can_be_freezed', lambda self: False):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertNotEqual(self.hero.companion, None)
        self.assertEqual(tt_api.load_cards(self.account_1.id), {})


    def test_use__no_companion_exists(self):

        card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=True)

        self.assertEqual(self.hero.companion, None)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(self.hero.companion, None)

        self.assertEqual(tt_api.load_cards(self.account_1.id), {})
