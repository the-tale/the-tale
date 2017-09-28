import uuid

from django.conf import settings as project_settings

from dext.common.utils.urls import url
from dext.common.utils import s11n

from the_tale.common.utils import tt_api
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.cards import conf

from . import cards
from . import objects
from . import relations


def get_card_url():
    return url('game:cards:api-get', api_version=conf.settings.GET_API_VERSION, api_client=project_settings.API_CLIENT)

def combine_cards_url():
    return url('game:cards:api-combine', api_version=conf.settings.COMBINE_API_VERSION, api_client=project_settings.API_CLIENT)


def move_to_storage_url():
    return url('game:cards:api-move-to-storage', api_version=conf.settings.MOVE_TO_STORAGE_API_VERSION, api_client=project_settings.API_CLIENT)


def move_to_hand_url():
    return url('game:cards:api-move-to-hand', api_version=conf.settings.MOVE_TO_HAND_API_VERSION, api_client=project_settings.API_CLIENT)


def use_card_url(card_uid):
    return url('game:cards:api-use', card=card_uid, api_version=conf.settings.USE_API_VERSION, api_client=project_settings.API_CLIENT)


def get_cards_url():
    return url('game:cards:api-get-cards', api_version=conf.settings.GET_CARDS_API_VERSION, api_client=project_settings.API_CLIENT)


def transform_cards_url():
    return url('game:cards:api-combine', api_version=conf.settings.COMBINE_API_VERSION, api_client=project_settings.API_CLIENT)


def create_card(allow_premium_cards, rarity=None, exclude=(), available_for_auction=False):
    from the_tale.game.cards import effects

    cards_types = list(cards.CARD.records)

    if not allow_premium_cards:
        cards_types = [card for card in cards_types if not card.availability.is_FOR_PREMIUMS]

    if rarity:
        cards_types = [card for card in cards_types if card.rarity == rarity]

    cards_choices = [card.effect.create_card(available_for_auction=available_for_auction, type=card)
                     for card in cards_types
                     if card.effect.available(card)]

    if exclude:
        cards_choices = [card for card in cards_choices if not any(card.is_same_effect(excluded_card) for excluded_card in exclude)]

    prioritites = [(card, card.type.rarity.priority) for card in cards_choices]

    return random_value_by_priority(prioritites)


def get_combined_card(allow_premium_cards, combined_cards):
    if not combined_cards:
        return None, relations.COMBINED_CARD_RESULT.NO_CARDS

    if len({card.type.rarity for card in combined_cards}) != 1:
        return None, relations.COMBINED_CARD_RESULT.EQUAL_RARITY_REQUIRED

    if len(combined_cards) != len({card.uid for card in combined_cards}):
        return None, relations.COMBINED_CARD_RESULT.DUPLICATE_IDS

    available_for_auction = all(card.available_for_auction for card in combined_cards)

    if len(combined_cards) == 1:
        return get_combined_card_1(combined_cards, allow_premium_cards, available_for_auction)

    if len(combined_cards) == 2:
        return get_combined_card_2(combined_cards, allow_premium_cards, available_for_auction)

    if len(combined_cards) == 3:
        return get_combined_card_3(combined_cards, allow_premium_cards, available_for_auction)

    return None, relations.COMBINED_CARD_RESULT.TOO_MANY_CARDS


def get_combined_card_1(combined_cards, allow_premium_cards, available_for_auction):
    if combined_cards[0].type.rarity.is_COMMON:
        return None, relations.COMBINED_CARD_RESULT.COMBINE_1_COMMON

    card = create_card(allow_premium_cards=allow_premium_cards,
                       rarity=relations.RARITY(combined_cards[0].type.rarity.value-1),
                       available_for_auction=available_for_auction)

    return card, relations.COMBINED_CARD_RESULT.SUCCESS


def get_combined_card_2(combined_cards, allow_premium_cards, available_for_auction):

    for reactor in combined_cards[0].type.combiners:
        card = reactor.combine(combined_cards)
        if card:
            return card, relations.COMBINED_CARD_RESULT.SUCCESS

    card = create_card(allow_premium_cards=allow_premium_cards,
                       rarity=combined_cards[0].type.rarity,
                       exclude=combined_cards,
                       available_for_auction=available_for_auction)

    return card, relations.COMBINED_CARD_RESULT.SUCCESS



def get_combined_card_3(combined_cards, allow_premium_cards, available_for_auction):

    for reactor in combined_cards[0].type.combiners:
        card = reactor.combine(combined_cards)
        if card:
            return card, relations.COMBINED_CARD_RESULT.SUCCESS

    if combined_cards[0].type.rarity.is_LEGENDARY:
        return None, relations.COMBINED_CARD_RESULT.COMBINE_3_LEGENDARY

    card = create_card(allow_premium_cards=allow_premium_cards,
                       rarity=relations.RARITY(combined_cards[0].type.rarity.value+1),
                       available_for_auction=available_for_auction)

    return card, relations.COMBINED_CARD_RESULT.SUCCESS


def get_cards_info_by_full_types():
    cards_info = {}

    for card in cards.CARD.records:
        names = card.effect.full_type_names(card)

        for full_type, name in names.items():
            cards_info[full_type] = {'name': name, 'card': card}

    return cards_info
