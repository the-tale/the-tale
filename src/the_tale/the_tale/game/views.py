# coding: utf-8

from dext.common.utils import views as dext_views
from dext.common.utils.urls import url

from the_tale.amqp_environment import environment

from the_tale.common.utils import api
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views
from the_tale.accounts.clans.prototypes import ClanPrototype

from the_tale.game.heroes import tt_api as heroes_tt_api
from the_tale.game.heroes import views as heroes_views
from the_tale.game.heroes.relations import EQUIPMENT_SLOT

from the_tale.game.map.conf import map_settings
from the_tale.game.map.storage import map_info_storage

from the_tale.game.conf import game_settings
from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game import logic as game_logic

from the_tale.game.cards.cards import CARD

from the_tale.game.abilities.relations import ABILITY_TYPE


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='game')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(heroes_views.CurrentHeroProcessor())

########################################
# views
########################################


@accounts_views.LoginRequiredProcessor()
@resource('')
def game_page(context):

    battle = Battle1x1Prototype.get_by_account_id(context.account.id)

    if battle and battle.state.is_PROCESSING:
        return dext_views.Redirect(url('game:pvp:'))

    clan = None
    if context.account.clan_id is not None:
        clan = ClanPrototype.get_by_id(context.account.clan_id)

    cards = sorted(CARD.records, key=lambda r: (r.rarity.value, r.text))

    return dext_views.Page('game/game_page.html',
                           content={'map_settings': map_settings,
                                    'game_settings': game_settings,
                                    'EQUIPMENT_SLOT': EQUIPMENT_SLOT,
                                    'current_map_version': map_info_storage.version,
                                    'clan': clan,
                                    'CARDS': cards,
                                    'resource': context.resource,
                                    'hero': context.account_hero,
                                    'ABILITY_TYPE': ABILITY_TYPE})


@api.Processor(versions=(game_settings.INFO_API_VERSION, '1.8', '1.7', '1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'))
@dext_views.IntsArgumentProcessor(error_message='Неверный формат номера хода', get_name='client_turns', context_name='client_turns', default_value=None)
@accounts_views.AccountProcessor(error_message='Запрашиваемый Вами аккаунт не найден', get_name='account', context_name='requested_account', default_value=None)
@resource('api', 'info', name='api-info')
def api_info(context):
    account = context.requested_account

    if account is None and context.account.is_authenticated:
        account = context.account

    data = game_logic.form_game_info(account=account,
                                     is_own=False if account is None else (context.account.id == account.id),
                                     client_turns=context.client_turns)

    if context.api_version in ('1.8', '1.7', '1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_9_to_1_8(data)

    if context.api_version in ('1.7', '1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_8_to_1_7(data)

    if context.api_version in ('1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_7_to_1_6(data)

    if context.api_version in ('1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_6_to_1_5(data)

    if context.api_version in ('1.4', '1.3', '1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_5_to_1_4(data)

    if context.api_version in ('1.3', '1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_4_to_1_3(data)

    if context.api_version in ('1.2', '1.1', '1.0'):
        data = game_logic.game_info_from_1_3_to_1_2(data)

    if context.api_version in ('1.1', '1.0'):
        data = game_logic.game_info_from_1_2_to_1_1(data)

    if context.api_version == '1.0':
        data = game_logic.game_info_from_1_1_to_1_0(data)

    return dext_views.AjaxOk(content=data)


@api.Processor(versions=(game_settings.DIARY_API_VERSION,))
@accounts_views.LoginRequiredProcessor()
@resource('api', 'diary', name='api-diary')
def api_diary(context):
    pb_diary = heroes_tt_api.get_diary(context.account.id)

    data = {'version': pb_diary.version,
            'messages': []}

    for pb_message in pb_diary.messages:
        data['messages'].append({'timestamp': pb_message.timestamp,
                                 'game_time': pb_message.game_time,
                                 'game_date': pb_message.game_date,
                                 'message':   pb_message.message,
                                 'type': pb_message.type,
                                 'variables': dict(pb_message.variables),
                                 'position': pb_message.position})

    return dext_views.AjaxOk(content=data)


@dext_views.DebugProcessor()
@accounts_views.LoginRequiredProcessor()
@accounts_views.SuperuserProcessor()
@resource('next-turn', method='POST')
def next_turn(context):
    environment.workers.supervisor.cmd_next_turn()
    return dext_views.AjaxOk()
