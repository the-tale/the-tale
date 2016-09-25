# coding: utf-8


from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.cards import relations
from the_tale.game.cards import objects
from the_tale.game.cards import goods_types



class CardsGoodTypeTests(testcase.TestCase):


    def setUp(self):
        super(CardsGoodTypeTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.hero_1 = self.storage.load_account_data(self.account_1)

        self.container = self.hero_1.cards

        self.card_1 = objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON, available_for_auction=True)
        self.card_2 = objects.Card(relations.CARD_TYPE.ADD_GOLD_UNCOMMON, available_for_auction=False)
        self.card_3 = objects.Card(relations.CARD_TYPE.ADD_GOLD_RARE, available_for_auction=True)
        self.card_4 = objects.Card(relations.CARD_TYPE.LEVEL_UP, available_for_auction=False)

        self.container.add_card(self.card_1)
        self.container.add_card(self.card_2)
        self.container.add_card(self.card_3)
        self.container.add_card(self.card_4)


    def test_instance(self):
        self.assertEqual(goods_types.cards_hero_good.uid, 'cards-hero-good')
        self.assertEqual(goods_types.cards_hero_good.item_uid_prefix, 'cards#')


    def test_create_good(self):
        good = goods_types.cards_hero_good.create_good(self.card_4)

        self.assertEqual(good.uid, 'cards#%d' % self.card_4.uid)
        self.assertEqual(good.name, self.card_4.name)
        self.assertEqual(good.type, goods_types.cards_hero_good.uid)
        self.assertEqual(good.item, self.card_4)


    def test_all_goods(self):
        self.assertEqual([good.item for good in goods_types.cards_hero_good.all_goods(self.hero_1)],
                         [self.card_1, self.card_3])


    def test_serialize_item(self):
        self.assertEqual(self.card_3.serialize(), goods_types.cards_hero_good.serialize_item(self.card_3))


    def test_deserialize_item(self):
        self.assertEqual(self.card_3, goods_types.cards_hero_good.deserialize_item(self.card_3.serialize()))

    def test_groups(self):
        self.assertEqual(len(goods_types.cards_hero_good.groups), 5)

    def test_group_of(self):
        for card_type in relations.CARD_TYPE.records:
            card = objects.Card(card_type, available_for_auction=False)
            self.assertEqual(goods_types.cards_hero_good.group_of(card).id, card.type.rarity.value)


    def test_is_item_tradable(self):
        self.assertTrue(goods_types.cards_hero_good.is_item_tradable(self.card_1))
        self.assertFalse(goods_types.cards_hero_good.is_item_tradable(self.card_2))


    def test_has_good(self):
        good = goods_types.cards_hero_good.create_good(self.card_1)

        self.assertTrue(goods_types.cards_hero_good.has_good(self.hero_1, good.uid))
        self.assertTrue(goods_types.cards_hero_good.has_good(self.hero_1, good.uid))
        self.assertFalse(goods_types.cards_hero_good.has_good(self.hero_1, '666'))


    def test_extract_good(self):
        good = goods_types.cards_hero_good.create_good(self.card_3)

        goods_types.cards_hero_good.extract_good(self.hero_1, good.uid)
        self.assertFalse(self.container.has_card(self.card_3.uid))


    def test_insert_good(self):
        card = objects.Card(relations.CARD_TYPE.CHANGE_ABILITIES_CHOICES, available_for_auction=False)
        good = goods_types.cards_hero_good.create_good(card)

        goods_types.cards_hero_good.insert_good(self.hero_1, good)
        self.assertTrue(self.container.has_card(card.uid))
