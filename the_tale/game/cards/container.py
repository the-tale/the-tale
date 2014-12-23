# coding: utf-8

from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.cards import relations
from the_tale.game.cards import exceptions
from the_tale.game.cards import objects


class CardsContainer(object):

    __slots__ = ('updated', '_cards', '_hero', '_help_count', '_premium_help_count', '_next_uid')

    def __init__(self, hero=None):
        self.updated = False
        self._cards = {}
        self._hero = hero
        self._help_count = 0
        self._premium_help_count = 0
        self._next_uid = 0

    def _get_next_uid(self):
        self._next_uid += 1
        return self._next_uid

    @property
    def help_count(self): return self._help_count

    def serialize(self):
        return {'cards': [card.serialize() for card in self._cards.itervalues()],
                'next_uid': self._next_uid,
                'help_count': self._help_count,
                'premium_help_count': self._premium_help_count}

    @classmethod
    def deserialize(cls, hero, data):
        obj = cls()
        obj._cards = {}

        for card_data in data.get('cards', ()):
            card = objects.Card.deserialize(card_data)
            obj._cards[card.uid] = card

        obj._hero = hero
        obj._help_count = data.get('help_count', 0)
        obj._premium_help_count = data.get('premium_help_count', 0)
        obj._next_uid = data.get('next_uid', 0)
        return obj

    # TODO
    # def ui_info(self):
    #     return {'cards': {card_type.value: count for card_type, count in self._cards.iteritems()},
    #             'help_count': self._help_count,
    #             'help_barrier': c.CARDS_HELP_COUNT_TO_NEW_CARD }

    def add_card(self, card):
        self.updated = True
        card.uid = self._get_next_uid()
        self._cards[card.uid] = card


    def remove_card(self, card_uid):
        self.updated = True

        if card_uid not in self._cards:
            raise exceptions.RemoveUnexistedCardError(card_uid=card_uid)

        del self._cards[card_uid]


    def cards_count(self):
        return len(self._cards)

    def all_cards(self): return sorted(self._cards.itervalues(), key=lambda x: x.type.text)

    def card_count(self, card_type):
        return len([card for card in self._cards.itervalues() if card.type == card_type])

    def has_card(self, card_type): return self.card_count(card_type) > 0

    @property
    def has_cards(self): return bool(self._cards)

    def change_help_count(self, delta):
        if self._help_count + delta < 0:
            raise exceptions.HelpCountBelowZero(current_value=self._help_count, delta=delta)

        self._help_count += delta

        if delta > 0 and self._hero.is_premium:
            self._premium_help_count += delta

        if delta < 0:
            self._premium_help_count = min(self._help_count, self._premium_help_count)


    def get_new_card(self, rarity=None, exclude=()):
        cards_types = relations.CARD_TYPE.records

        if not self._hero.is_premium:
            cards_types = [card for card in cards_types if not card.availability.is_FOR_PREMIUMS]

        if rarity:
            cards_types = [card for card in cards_types if card.rarity == rarity]

        if exclude:
            cards_types = [card for card in cards_types if card not in exclude]

        prioritites = [(card, card.rarity.priority) for card in cards_types]

        card_type = random_value_by_priority(prioritites)

        card = objects.Card(type=card_type, available_for_auction=self._hero.is_premium)

        self.add_card(card)

        return card


    def can_combine_cards(self, cards_uids):
        if any(uid not in self._cards for uid in cards_uids):
            return relations.CARDS_COMBINING_STATUS.HAS_NO_CARDS

        cards = [self._cards[uid] for uid in cards_uids]

        if len(cards) < 2:
            return relations.CARDS_COMBINING_STATUS.NOT_ENOUGH_CARDS

        if len(cards) > 3:
            return relations.CARDS_COMBINING_STATUS.TO_MANY_CARDS

        rarities = set([card.type.rarity for card in cards])

        if len(rarities) != 1:
            return relations.CARDS_COMBINING_STATUS.EQUAL_RARITY_REQUIRED

        if list(rarities)[0].is_LEGENDARY and len(cards) == 3:
            return relations.CARDS_COMBINING_STATUS.LEGENDARY_X3_DISALLOWED

        return relations.CARDS_COMBINING_STATUS.ALLOWED


    def get_card_for_use(self, card_type):
        choices = [card for card in self._cards.itervalues() if card.type == card_type]

        if not choices:
            return None

        not_auction_choices = [card for card in choices if not card.available_for_auction]

        if not_auction_choices:
            return not_auction_choices[0]

        return choices[0]
