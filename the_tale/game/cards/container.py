# coding: utf-8

from the_tale.game.cards import relations
from the_tale.game.cards import exceptions


class CardsContainer(object):

    __slots__ = ('updated', '_cards')

    def __init__(self):
        self.updated = False
        self._cards = {}

    def serialize(self):
        return {'cards': {card_type.value: count for card_type, count in self._cards.iteritems()} }

    @classmethod
    def deserialize(cls, hero, data):
        obj = cls()
        obj._cards = {relations.CARD_TYPE(int(card_type)): count for card_type, count in data.get('cards', {}).iteritems()}
        return obj

    def ui_info(self):
        return {'cards': {card_type.value: count for card_type, count in self._cards.iteritems()} }

    def add_card(self, card_type, count):
        self.updated = True

        if card_type in self._cards:
            self._cards[card_type] += count
        else:
            self._cards[card_type] = count


    def remove_card(self, card_type, count):
        self.updated = True

        if self._cards.get(card_type, 0) < count:
            raise exceptions.RemoveUnexistedCardError(card=card_type, count=count)

        self._cards[card_type] -= count

        if not self._cards[card_type]:
            del self._cards[card_type]

    @property
    def cards(self): return sorted(self._cards.iteritems(), key=lambda x: x[0].text)

    def card_count(self, card_type): return self._cards.get(card_type, 0)

    @property
    def has_cards(self): return len(self._cards)
