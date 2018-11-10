
import smart_imports

smart_imports.all()


def use_ability_url(ability, building=None, battle=None):
    if building is not None:
        return dext_urls.url('game:abilities:use', ability.value, api_version='1.0', api_client=django_settings.API_CLIENT, building=building.id)
    if battle is not None:
        return dext_urls.url('game:abilities:use', ability.value, api_version='1.0', api_client=django_settings.API_CLIENT, battle=battle.id)
    return dext_urls.url('game:abilities:use', ability.value, api_version='1.0', api_client=django_settings.API_CLIENT)
