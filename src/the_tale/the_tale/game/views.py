
import itertools

from dext.common.utils import views as dext_views
from dext.common.utils.urls import url

from tt_logic.beings import relations as beings_relations

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

from . import names
from . import relations


class NameProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'name_forms'
    ERROR_MESSAGE = 'Ошибка при передаче имени героя'
    POST_NAME = 'name'

    def parse(self, context, raw_value):
        raw_value = raw_value.split(',')

        if len(raw_value) != 6:
            self.raise_wrong_format()

        for value in raw_value:
            if not isinstance(value, str):
                self.raise_wrong_format()

        return raw_value


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


@api.Processor(versions=(game_settings.NAMES_API_VERSION,))
@dext_views.IntArgumentProcessor(error_message='Неверное количество имён', get_name='number', context_name='names_number', default_value=None)
@resource('api', 'names', name='api-names')
def api_names(context):

    if context.names_number < 0 or 100 < context.names_number:
        raise dext_views.ViewError(code='wrong_number', message='Нельзя сгенерировать такое колдичесво имён')

    result_names = names.get_names_set(number=context.names_number)

    return dext_views.AjaxOk(content={'names': result_names})


@dext_views.RelationArgumentProcessor(relation=relations.GENDER, error_message='Неверно указан пол героя',
                                      context_name='gender', post_name='gender')
@dext_views.RelationArgumentProcessor(relation=relations.RACE, error_message='Неверно указана раса героя',
                                      context_name='race', post_name='race')
@dext_views.RelationArgumentProcessor(relation=relations.ARCHETYPE, error_message='Неверно указана архетип героя',
                                      context_name='archetype', post_name='archetype')
@dext_views.RelationArgumentProcessor(relation=relations.HABIT_HONOR_INTERVAL, error_message='Неверно указана честь героя',
                                      context_name='honor', post_name='honor')
@dext_views.RelationArgumentProcessor(relation=relations.HABIT_PEACEFULNESS_INTERVAL, error_message='Неверно указано миролюбие героя',
                                      context_name='peacefulness', post_name='peacefulness')
@dext_views.RelationArgumentProcessor(relation=beings_relations.UPBRINGING, error_message='Неверно указано происхождение героя',
                                      context_name='upbringing', post_name='upbringing')
@dext_views.RelationArgumentProcessor(relation=beings_relations.FIRST_DEATH, error_message='Неверно указана первая смерть героя',
                                      context_name='first_death', post_name='first_death')
@dext_views.RelationArgumentProcessor(relation=beings_relations.AGE, error_message='Неверно указан возраст первой смерти героя',
                                      context_name='age', post_name='age')
@NameProcessor()
@api.Processor(versions=(game_settings.HERO_HISTORY_API_VERSION,))
@resource('api', 'hero-history', method='POST', name='api-hero-history')
def api_hero_history(context):
    texts = game_logic.generate_history(name_forms=context.name_forms,
                                        gender=context.gender,
                                        race=context.race,
                                        honor=context.honor,
                                        peacefulness=context.peacefulness,
                                        archetype=context.archetype,
                                        upbringing=context.upbringing,
                                        first_death=context.first_death,
                                        age=context.age)

    return dext_views.AjaxOk(content={'story': texts})


@accounts_views.LoginRequiredProcessor()
@resource('hero-history-status')
def hero_history_status(context):

    properties = itertools.product(relations.GENDER.records,
                                   relations.RACE.records,
                                   [relations.HABIT_HONOR_INTERVAL.LEFT_1, relations.HABIT_HONOR_INTERVAL.RIGHT_1],
                                   [relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1, relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1],
                                   relations.ARCHETYPE.records,
                                   beings_relations.UPBRINGING.records,
                                   beings_relations.FIRST_DEATH.records,
                                   beings_relations.AGE.records)

    misses = [[], [], []]

    for property_vector in properties:
        texts = game_logic.generate_history(['test']*6, *property_vector)

        for i, text in enumerate(texts):
            if text is None:
                misses[i].append(', '.join([property.text for property in property_vector]))

    return dext_views.Page('game/hero_history_status.html',
                           content={'resource': context.resource,
                                    'misses': misses})


@dext_views.DebugProcessor()
@accounts_views.LoginRequiredProcessor()
@accounts_views.SuperuserProcessor()
@resource('next-turn', method='POST')
def next_turn(context):
    environment.workers.supervisor.cmd_next_turn()
    return dext_views.AjaxOk()
