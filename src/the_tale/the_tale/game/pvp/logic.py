
import smart_imports

smart_imports.all()


def pvp_page_url():
    return dext_urls.url('game:pvp:')


def pvp_info_url():
    return dext_urls.url('game:pvp:api-info',
                         api_version=conf.settings.INFO_API_VERSION,
                         api_client=django_settings.API_CLIENT)


def pvp_call_to_arena_url():
    return dext_urls.url('game:pvp:api-call-to-arena',
                         api_version=conf.settings.CALL_TO_ARENA_API_VERSION,
                         api_client=django_settings.API_CLIENT)


def pvp_leave_arena_url():
    return dext_urls.url('game:pvp:api-leave-arena',
                         api_version=conf.settings.LEAVE_ARENA_API_VERSION,
                         api_client=django_settings.API_CLIENT)


def pvp_accept_arena_battle_url(battle_request_id=None):
    arguments = {'api_version': conf.settings.ACCEPT_ARENA_BATTLE_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    if battle_request_id is not None:
        arguments['battle_request_id'] = battle_request_id

    return dext_urls.url('game:pvp:api-accept-arena-battle',
                         **arguments)


def pvp_create_arena_bot_battle_url():
    return dext_urls.url('game:pvp:api-create-arena-bot-battle',
                         api_version=conf.settings.CREATE_ARENA_BOT_BATTLE_API_VERSION,
                         api_client=django_settings.API_CLIENT)


def initiate_battle(initiator_id, acceptor_id, battle_id):

    initiator = accounts_prototypes.AccountPrototype.get_by_id(initiator_id)
    acceptor = accounts_prototypes.AccountPrototype.get_by_id(acceptor_id)

    logging.info('start battle between initiaor %d and acceptor %d' % (initiator_id, acceptor_id))

    task = game_prototypes.SupervisorTaskPrototype.create_arena_pvp_1x1(initiator, acceptor)

    amqp_environment.environment.workers.supervisor.cmd_add_task(task.id)

    return task


def arena_info():
    from the_tale.game import logic as game_logic

    battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=(relations.MATCHMAKER_TYPE.ARENA,
                                                                                            relations.MATCHMAKER_TYPE.BOT))

    requests = [request for request in battle_requests if request.matchmaker_type.is_ARENA]
    requests.sort(key=lambda request: request.created_at)

    data = {'arena_battle_requests': [request.ui_info() for request in requests],
            'active_bot_battles': active_battles[relations.MATCHMAKER_TYPE.BOT],
            'active_arena_battles': active_battles[relations.MATCHMAKER_TYPE.ARENA]}

    accounts_ids = {request.initiator_id for request in battle_requests}

    data['accounts'] = game_logic.accounts_info(accounts_ids)
    data['clans'] = game_logic.clans_info(data['accounts'])

    return data


def get_enemy_id(account_id):
    battles = tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(account_id,))

    if not battles:
        return None

    participants_ids = set(battles[0].participants_ids)
    participants_ids.remove(account_id)

    return list(participants_ids)[0]


def get_arena_heroes(hero):

    if hero.actions.current_action.meta_action is None:
        return hero, None

    if hero.actions.current_action.meta_action.hero_1_id == hero.id:
        hero = hero.actions.current_action.meta_action.hero_1
        enemy = hero.actions.current_action.meta_action.hero_2

    else:
        hero = hero.actions.current_action.meta_action.hero_2
        enemy = hero.actions.current_action.meta_action.hero_1

    return hero, enemy


def get_arena_heroes_pvp(hero):

    if hero.actions.current_action.meta_action is None:
        return None, None

    if hero.actions.current_action.meta_action.hero_1_id == hero.id:
        hero_pvp = hero.actions.current_action.meta_action.hero_1_pvp
        enemy_pvp = hero.actions.current_action.meta_action.hero_2_pvp

    else:
        hero_pvp = hero.actions.current_action.meta_action.hero_2_pvp
        enemy_pvp = hero.actions.current_action.meta_action.hero_1_pvp

    return hero_pvp, enemy_pvp


def calculate_rating_required(hero, enemy_hero):
    if hero.is_bot or enemy_hero.is_bot:
        return False

    return abs(hero.level - enemy_hero.level) <= conf.settings.MAX_RATING_LEVEL_DELTA
