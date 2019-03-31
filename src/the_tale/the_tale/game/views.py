
import smart_imports

smart_imports.all()


class NameProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'name_forms'
    ERROR_MESSAGE = 'Ошибка при передаче имени героя'
    POST_NAME = 'name'

    def parse(self, context, raw_value):
        forms = raw_value.split(',')

        if len(forms) != 6:
            self.raise_wrong_format()

        success, message = heroes_logic.validate_name(forms)

        if not success:
            self.raise_wrong_format()

        return forms


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

    battle = pvp_prototypes.Battle1x1Prototype.get_by_account_id(context.account.id)

    if battle and battle.state.is_PROCESSING:
        return dext_views.Redirect(dext_urls.url('game:pvp:'))

    clan = None
    if context.account.clan_id is not None:
        clan = clans_logic.load_clan(clan_id=context.account.clan_id)

    cards = sorted(cards_types.CARD.records, key=lambda r: (r.rarity.value, r.text))

    return dext_views.Page('game/game_page.html',
                           content={'map_settings': map_conf.settings,
                                    'game_settings': conf.settings,
                                    'EQUIPMENT_SLOT': heroes_relations.EQUIPMENT_SLOT,
                                    'current_map_version': map_storage.map_info.version,
                                    'clan': clan,
                                    'CARDS': cards,
                                    'resource': context.resource,
                                    'hero': context.account_hero,
                                    'ABILITY_TYPE': abilities_relations.ABILITY_TYPE})


@utils_api.Processor(versions=(conf.settings.INFO_API_VERSION, '1.8', '1.7', '1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'))
@dext_views.IntsArgumentProcessor(error_message='Неверный формат номера хода', get_name='client_turns', context_name='client_turns', default_value=None)
@accounts_views.AccountProcessor(error_message='Запрашиваемый Вами аккаунт не найден', get_name='account', context_name='requested_account', default_value=None)
@resource('api', 'info', name='api-info')
def api_info(context):
    account = context.requested_account

    if account is None and context.account.is_authenticated:
        account = context.account

    data = logic.form_game_info(account=account,
                                is_own=False if account is None else (context.account.id == account.id),
                                client_turns=context.client_turns)

    if context.api_version in ('1.8', '1.7', '1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_9_to_1_8(data)

    if context.api_version in ('1.7', '1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_8_to_1_7(data)

    if context.api_version in ('1.6', '1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_7_to_1_6(data)

    if context.api_version in ('1.5', '1.4', '1.3', '1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_6_to_1_5(data)

    if context.api_version in ('1.4', '1.3', '1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_5_to_1_4(data)

    if context.api_version in ('1.3', '1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_4_to_1_3(data)

    if context.api_version in ('1.2', '1.1', '1.0'):
        data = logic.game_info_from_1_3_to_1_2(data)

    if context.api_version in ('1.1', '1.0'):
        data = logic.game_info_from_1_2_to_1_1(data)

    if context.api_version == '1.0':
        data = logic.game_info_from_1_1_to_1_0(data)

    return dext_views.AjaxOk(content=utils_api.olbanize(data))


@utils_api.Processor(versions=(conf.settings.DIARY_API_VERSION,))
@accounts_views.LoginRequiredProcessor()
@resource('api', 'diary', name='api-diary')
def api_diary(context):
    diary = heroes_tt_services.diary.cmd_diary(context.account.id)

    return dext_views.AjaxOk(content=utils_api.olbanize(diary))


@utils_api.Processor(versions=(conf.settings.NAMES_API_VERSION,))
@dext_views.IntArgumentProcessor(error_message='Неверное количество имён', get_name='number', context_name='names_number', default_value=None)
@resource('api', 'names', name='api-names')
def api_names(context):

    if context.names_number < 0 or 100 < context.names_number:
        raise dext_views.ViewError(code='wrong_number', message='Нельзя сгенерировать такое колдичесво имён')

    result_names = game_names.get_names_set(number=context.names_number)

    return dext_views.AjaxOk(content={'names': utils_api.olbanize(result_names)})


@accounts_views.hero_story_attributes
@utils_api.Processor(versions=(conf.settings.HERO_HISTORY_API_VERSION,))
@resource('api', 'hero-history', method='POST', name='api-hero-history')
def api_hero_history(context):
    texts = logic.generate_history(name_forms=context.name_forms,
                                   gender=context.gender,
                                   race=context.race,
                                   honor=context.honor,
                                   peacefulness=context.peacefulness,
                                   archetype=context.archetype,
                                   upbringing=context.upbringing,
                                   first_death=context.first_death,
                                   age=context.age)

    return dext_views.AjaxOk(content={'story': utils_api.olbanize(texts)})


@accounts_views.LoginRequiredProcessor()
@resource('hero-history-status')
def hero_history_status(context):

    properties = itertools.product(relations.GENDER.records,
                                   relations.RACE.records,
                                   [relations.HABIT_HONOR_INTERVAL.LEFT_1, relations.HABIT_HONOR_INTERVAL.RIGHT_1],
                                   [relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1, relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1],
                                   relations.ARCHETYPE.records,
                                   tt_beings_relations.UPBRINGING.records,
                                   tt_beings_relations.FIRST_DEATH.records,
                                   tt_beings_relations.AGE.records)

    misses = [[], [], []]

    for property_vector in properties:
        texts = logic.generate_history(['test'] * 6, *property_vector)

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
    amqp_environment.environment.workers.supervisor.cmd_next_turn()
    return dext_views.AjaxOk()
