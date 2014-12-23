# coding: utf-8
import collections

from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.balance import constants as c

from the_tale.game.cards import relations
from the_tale.game.cards import exceptions


class CardsContainer(object):

    __slots__ = ('updated', '_cards', '_hero', '_help_count')

    def __init__(self):
        self.updated = False
        self._cards = {}
        self._hero = None
        self._help_count = 0

    @property
    def help_count(self): return self._help_count

    def serialize(self):
        return {'cards': {card_type.value: count for card_type, count in self._cards.iteritems()} }

    @classmethod
    def deserialize(cls, hero, data):
        obj = cls()
        obj._cards = {relations.CARD_TYPE(int(card_type)): count for card_type, count in data.get('cards', {}).iteritems()}
        obj._hero = hero
        obj._help_count = data.get('help_count', 0)
        return obj

    def ui_info(self):
        return {'cards': {card_type.value: count for card_type, count in self._cards.iteritems()},
                'help_count': self._help_count,
                'help_barrier': c.CARDS_HELP_COUNT_TO_NEW_CARD }

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

    def cards_count(self):
        return sum(self._cards.values())

    @property
    def cards(self): return sorted(self._cards.iteritems(), key=lambda x: x[0].text)

    def card_count(self, card_type): return self._cards.get(card_type, 0)

    def has_card(self, card_type): return self._cards.get(card_type, 0) > 0

    @property
    def has_cards(self): return len(self._cards)

    def change_help_count(self, delta):
        self._help_count += delta

    def get_new_card(self, rarity=None, exclude=()):
        cards = relations.CARD_TYPE.records

        if not self._hero.is_premium:
            cards = [card for card in cards if not card.availability.is_FOR_PREMIUMS]

        if rarity:
            cards = [card for card in cards if card.rarity == rarity]

        if exclude:
            cards = [card for card in cards if card not in exclude]

        prioritites = [(card, card.rarity.priority) for card in cards]

        card = random_value_by_priority(prioritites)

        self.add_card(card, 1)

        return card

    def can_combine_cards(self, cards):
        if len(cards) < 2:
            return relations.CARDS_COMBINING_STATUS.NOT_ENOUGH_CARDS

        if len(cards) > 3:
            return relations.CARDS_COMBINING_STATUS.TO_MANY_CARDS

        rarities = set([card.rarity for card in cards])

        if len(rarities) != 1:
            return relations.CARDS_COMBINING_STATUS.EQUAL_RARITY_REQUIRED

        if list(rarities)[0].is_LEGENDARY and len(cards) == 3:
            return relations.CARDS_COMBINING_STATUS.LEGENDARY_X3_DISALLOWED

        cards_counter = collections.Counter(cards)

        if not all(self.card_count(card) >= cards_counter.get(card, 0) for card in cards):
            return relations.CARDS_COMBINING_STATUS.HAS_NO_CARDS

        return relations.CARDS_COMBINING_STATUS.ALLOWED
