# coding: utf-8

from django.conf import settings as project_settings

from dext.utils.urls import url


def use_ability_url(ability, building=None, battle=None):
    if building is not None:
        return url('game:abilities:use', ability.value, api_version='1.0', api_client=project_settings.API_CLIENT, building=building.id)
    if battle is not None:
        return url('game:abilities:use', ability.value, api_version='1.0', api_client=project_settings.API_CLIENT, battle=battle.id)
    return url('game:abilities:use', ability.value, api_version='1.0', api_client=project_settings.API_CLIENT)
