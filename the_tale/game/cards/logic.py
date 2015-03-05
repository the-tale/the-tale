# coding: utf-8

from django.conf import settings as project_settings

from dext.common.utils.urls import url

from the_tale.game.cards import effects
from the_tale.game.cards import conf


def create_card(type, available_for_auction):
    return effects.EFFECTS[type].create_card(available_for_auction=available_for_auction)


def get_card_url():
    return url('game:cards:api-get', api_version=conf.settings.GET_API_VERSION, api_client=project_settings.API_CLIENT)

def combine_cards_url(cards_uids=None):
    if cards_uids:
        return url('game:cards:api-combine', cards=','.join(str(card_uid) for card_uid in cards_uids),
                   api_version=conf.settings.COMBINE_API_VERSION, api_client=project_settings.API_CLIENT)

    return url('game:cards:api-combine', api_version=conf.settings.COMBINE_API_VERSION, api_client=project_settings.API_CLIENT)

def use_card_url(card_uid):
    return url('game:cards:api-use', card=card_uid, api_version=conf.settings.USE_API_VERSION, api_client=project_settings.API_CLIENT)
