# coding: utf-8

from the_tale.common.utils.decorators import lazy_property

from the_tale.market import goods_types
from the_tale.market import objects as market_objects

from the_tale.game.cards import objects
from the_tale.game.cards import relations


class CardsGoodType(goods_types.BaseGoodType):

    def create_good(self, item):
        good = market_objects.Good(type=self.uid,
                                   name=item.name,
                                   uid=self.item_uid_prefix + str(item.uid),
                                   item=item)
        return good

    def all_goods(self, container):
        goods = []

        for card in container.cards.all_cards():
            if card.available_for_auction:
                goods.append(self.create_good(card))

        return goods

    def serialize_item(self, item):
        return item.serialize()

    def deserialize_item(self, data):
        return objects.Card.deserialize(data)

    def is_item_tradable(self, item):
        return item.available_for_auction


    def _extract_card_uid(self, good_uid):
        try:
            return int(good_uid[len(self.item_uid_prefix):])
        except:
            return None

    def has_good(self, container, good_uid):
        return container.cards.has_card(self._extract_card_uid(good_uid))

    def extract_good(self, container, good_uid):
        container.cards.remove_card(self._extract_card_uid(good_uid))

    def insert_good(self, container, good):
        container.cards.add_card(good.item)

    @lazy_property
    def groups(self):
        return [goods_types.GoodsGroup(id=rarity.value, name=rarity.text, type=self) for rarity in relations.RARITY.records]

    def group_of(self, item):
        for group in self.groups:
            if item.type.rarity.value == group.id:
                return group

cards_hero_good = CardsGoodType(uid='cards-hero-good',
                                name=u'Карты Судьбы',
                                description=u'Карты Судьбы',
                                item_uid_prefix='cards#',
                                item_template='cards/card_template.html')
