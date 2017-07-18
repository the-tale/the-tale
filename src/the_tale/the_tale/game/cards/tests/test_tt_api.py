
import uuid
import collections

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.finances.market import goods_types

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions import models as companions_models
from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions.tests import helpers as companions_helpers

from .. import relations
from .. import exceptions
from .. import objects
from .. import effects
from .. import tt_api
from .. import cards


class TTAPiTests(testcase.TestCase):

    def setUp(self):
        super().setUp()
        create_test_map()
        tt_api.debug_clear_service()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)


        self.cards = [objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4()),
                      objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4()),
                      objects.Card(cards.CARD.KEEPERS_GOODS_LEGENDARY, uid=uuid.uuid4()),
                      cards.CARD.GET_COMPANION_UNCOMMON.effect.create_card(cards.CARD.GET_COMPANION_UNCOMMON, available_for_auction=True),
                      objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4()),
                      objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())]


    def test_load_no_cards(self):
        cards = tt_api.load_cards(666)
        self.assertEqual(cards, {})


    def fill_storage(self):
        tt_api.change_cards(account_id=666,
                            operation_type='#test',
                            to_add=[self.cards[0], self.cards[1], self.cards[3]],
                            to_remove=[])

        tt_api.change_cards(account_id=777,
                            operation_type='#test',
                            to_add=[self.cards[4]],
                            to_remove=[])

        tt_api.change_cards(account_id=666,
                            operation_type='#test',
                            to_add=[self.cards[2], self.cards[5]],
                            to_remove=[self.cards[1]])


    def test_change_and_load(self):
        self.fill_storage()

        cards = tt_api.load_cards(666)

        self.assertEqual(cards, {card.uid: card for card in [self.cards[0], self.cards[2], self.cards[3], self.cards[5]]})


    def test_has_card(self):
        self.fill_storage()

        self.assertTrue(tt_api.has_cards(666, [self.cards[0].uid, self.cards[3].uid]))
        self.assertFalse(tt_api.has_cards(666, [self.cards[0].uid, self.cards[4].uid]))
