# coding: utf-8
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.balance import constants as c

from the_tale.game.cards import relations
from the_tale.game.cards import exceptions
from the_tale.game.cards import objects
from the_tale.game.cards import goods_types
from the_tale.game.cards import logic
from the_tale.game.cards import effects


class CardsContainer(object):

    __slots__ = ('updated', '_cards', '_hero', '_help_count', '_premium_help_count', '_next_uid')

    def __init__(self):
        self.updated = False
        self._cards = {}
        self._hero = None
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
    def deserialize(cls, data):
        obj = cls()
        obj._cards = {}

        for card_data in data.get('cards', ()):
            card = objects.Card.deserialize(card_data)
            obj._cards[card.uid] = card

        obj._help_count = data.get('help_count', 0)
        obj._premium_help_count = data.get('premium_help_count', 0)
        obj._next_uid = data.get('next_uid', 0)
        return obj

    def ui_info(self):
        return {'cards': [card.ui_info() for card in self._cards.itervalues()],
                'help_count': self._help_count,
                'help_barrier': c.CARDS_HELP_COUNT_TO_NEW_CARD }

    @classmethod
    def ui_info_null(self):
        return {'cards': [],
                'help_count': 0,
                'help_barrier': c.CARDS_HELP_COUNT_TO_NEW_CARD }

    def add_card(self, card):
        self.updated = True
        card.uid = self._get_next_uid()
        self._cards[card.uid] = card
        goods_types.cards_hero_good.sync_added_item(self._hero.account_id, card)


    def remove_card(self, card_uid):
        self.updated = True

        if card_uid not in self._cards:
            raise exceptions.RemoveUnexistedCardError(card_uid=card_uid)

        goods_types.cards_hero_good.sync_removed_item(self._hero.account_id, self._cards[card_uid])

        del self._cards[card_uid]


    def cards_count(self):
        return len(self._cards)

    def all_cards(self): return self._cards.itervalues()

    def has_card(self, card_uid): return card_uid in self._cards

    @property
    def has_cards(self): return bool(self._cards)

    def change_help_count(self, delta):
        if self._help_count + delta < 0:
            raise exceptions.HelpCountBelowZero(current_value=self._help_count, delta=delta)

        self.updated = True

        self._help_count += delta

        if delta > 0 and self._hero.is_premium:
            self._premium_help_count += delta

        if delta < 0:
            self._premium_help_count = min(self._help_count, self._premium_help_count)


    def get_new_card(self, rarity=None, exclude=(), available_for_auction=None):
        cards_types = relations.CARD_TYPE.records

        if available_for_auction is None:
            available_for_auction=self._hero.is_premium

        if not self._hero.is_premium:
            cards_types = [card for card in cards_types if not card.availability.is_FOR_PREMIUMS]

        if rarity:
            cards_types = [card for card in cards_types if card.rarity == rarity]

        cards_choices = [logic.create_card(type=card_type, available_for_auction=available_for_auction)
                         for card_type in cards_types
                         if effects.EFFECTS[card_type].available()]

        if exclude:
            cards_choices = [card for card in cards_choices if not any(card.is_same_effect(excluded_card) for excluded_card in exclude)]

        prioritites = [(card, card.type.rarity.priority) for card in cards_choices]

        card = random_value_by_priority(prioritites)

        if card:
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

    def get_card(self, card_uid):
        return self._cards.get(card_uid)


    def combine_cards(self, cards_uids):
        '''
        here we expect that can_combine_cards was called and checked
        '''
        cards = [self.get_card(card_uid) for card_uid in cards_uids]

        for card_uid in cards_uids:
            self.remove_card(card_uid)

        if len(cards_uids) == 2:
            rarity = cards[0].type.rarity
        else:
            rarity=relations.RARITY(cards[0].type.rarity.value+1)

        card = self.get_new_card(rarity=rarity,
                                 exclude=[card for card in cards],
                                 available_for_auction=all(card.available_for_auction for card in cards))

        return card
