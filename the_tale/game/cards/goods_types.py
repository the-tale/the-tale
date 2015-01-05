# coding: utf-8

from the_tale.market import goods_types
from the_tale.market import objects as market_objects

from the_tale.game.cards import objects


class CardsGoodType(goods_types.BaseGoodType):

    def create_good(self, item):
        good = market_objects.Good(type=self.uid,
                                   name=item.name,
                                   uid=self.item_uid_prefix + str(item.uid),
                                   item=item)
        return good

    def serialize_item(self, item):
        return item.serialize()

    def deserialize_item(self, data):
        return objects.Card.deserialize(data)

    def has_good(self, container, good_uid):
        card_uid = int(good_uid[len(self.item_uid_prefix):])
        return container.cards.has_card(card_uid)

    def extract_good(self, container, good_uid):
        card_uid = int(good_uid[len(self.item_uid_prefix):])
        return container.cards.remove_card(card_uid)

    def insert_good(self, container, good):
        return container.cards.add_card(good.item)


cards_hero_good = CardsGoodType(uid='cards-hero-good', name=u'Карты Судьбы', description=u'Карты Судьбы', item_uid_prefix='cards#')
