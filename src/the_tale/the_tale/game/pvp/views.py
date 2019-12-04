
import smart_imports

smart_imports.all()


########################################
# processors definition
########################################

class CanParticipateInPvPProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'pvp.no_rights'
    ERROR_MESSAGE = 'Вы не можете отправить героя на арену. Для этого необходимо завершить регистрацию.'

    def check(self, context):
        return context.account_hero.can_participate_in_pvp


class AbilityProcessor(utils_views.ArgumentProcessor):
    GET_NAME = 'ability'
    CONTEXT_NAME = 'ability'
    DEFAULT_VALUE = None
    ERROR_MESSAGE = 'Неверный тип способности'

    def parse(self, context, raw_value):
        try:
            return abilities.ABILITIES[raw_value]
        except KeyError:
            self.raise_wrong_format()


class BattleRequestIdProcessor(utils_views.ArgumentProcessor):
    CONTEXT_NAME = 'battle_request_id'
    ERROR_MESSAGE = 'Неверный номер вызова на арену'
    GET_NAME = 'battle_request_id'

    def parse(self, context, raw_value):
        return int(raw_value)


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='pvp')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.LoginRequiredProcessor())
resource.add_processor(heroes_views.CurrentHeroProcessor())

########################################
# views
########################################


@CanParticipateInPvPProcessor()
@resource('')
def pvp_page(context):

    enemy_id = logic.get_enemy_id(context.account.id)

    if enemy_id is None:
        return utils_views.Redirect(django_reverse('game:'), permanent=False)

    own_abilities = sorted(context.account_hero.abilities.all, key=lambda x: x.NAME)

    enemy_account = accounts_prototypes.AccountPrototype.get_by_id(enemy_id)

    enemy_hero = heroes_logic.load_hero(account_id=enemy_id)
    enemy_abilities = sorted(enemy_hero.abilities.all, key=lambda x: x.NAME)

    say_form = forms.SayForm()

    clan = None
    if context.account.clan_id is not None:
        clan = clans_logic.load_clan(clan_id=context.account.clan_id)

    enemy_clan = None
    if enemy_account.clan_id is not None:
        enemy_clan = clans_logic.load_clan(clan_id=enemy_account.clan_id)

    calculate_rating = logic.calculate_rating_required(context.account_hero, enemy_hero)

    return utils_views.Page('pvp/pvp_page.html',
                            content={'enemy_account': accounts_prototypes.AccountPrototype.get_by_id(enemy_id),
                                     'own_hero': context.account_hero,
                                     'own_abilities': own_abilities,
                                     'enemy_abilities': enemy_abilities,
                                     'game_settings': game_conf.settings,
                                     'say_form': say_form,
                                     'clan': clan,
                                     'enemy_clan': enemy_clan,
                                     'calculate_rating': calculate_rating,
                                     'EQUIPMENT_SLOT': heroes_relations.EQUIPMENT_SLOT,
                                     'ABILITIES': (abilities.Ice, abilities.Blood, abilities.Flame),
                                     'resource': context.resource})


@CanParticipateInPvPProcessor()
@utils_views.FormProcessor(form_class=forms.SayForm)
@resource('say', method='post')
def say(context):
    say_task = postponed_tasks.SayInBattleLogTask(speaker_id=context.account.id,
                                                  text=context.form.c.text)

    task = PostponedTaskPrototype.create(say_task)

    amqp_environment.environment.workers.supervisor.cmd_logic_task(context.account.id, task.id)

    return utils_views.AjaxProcessing(task.status_url)


@CanParticipateInPvPProcessor()
@AbilityProcessor()
@resource('use-ability', method='post')
def use_ability(context):
    use_ability_task = postponed_tasks.UsePvPAbilityTask(account_id=context.account.id,
                                                         ability_id=context.ability.TYPE)

    task = PostponedTaskPrototype.create(use_ability_task)

    amqp_environment.environment.workers.supervisor.cmd_logic_task(context.account.id, task.id)

    return utils_views.AjaxProcessing(task.status_url)


@CanParticipateInPvPProcessor()
@utils_api.Processor(versions=(conf.settings.CALL_TO_ARENA_API_VERSION,))
@resource('api', 'call-to-arena', method='post', name='api-call-to-arena')
def call_to_arena(context):

    tt_services.matchmaker.cmd_create_battle_request(matchmaker_type=relations.MATCHMAKER_TYPE.ARENA,
                                                     initiator_id=context.account.id)

    return utils_views.AjaxOk(content={'info': logic.arena_info()})


@CanParticipateInPvPProcessor()
@utils_api.Processor(versions=(conf.settings.LEAVE_ARENA_API_VERSION,))
@resource('api', 'leave-arena', method='post', name='api-leave-arena')
def leave_arena(context):

    battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=(relations.MATCHMAKER_TYPE.ARENA,))

    for request in battle_requests:
        if request.initiator_id != context.account.id:
            continue

        tt_services.matchmaker.cmd_cancel_battle_request(battle_request_id=request.id)

        break

    return utils_views.AjaxOk(content={'info': logic.arena_info()})


@CanParticipateInPvPProcessor()
@BattleRequestIdProcessor()
@utils_api.Processor(versions=(conf.settings.ACCEPT_ARENA_BATTLE_API_VERSION,))
@resource('api', 'accept-arena-battle', method='post', name='api-accept-arena-battle')
def accept_arena_battle(context):

    result, battle_id, participants_ids = tt_services.matchmaker.cmd_accept_battle_request(battle_request_id=context.battle_request_id,
                                                                                           acceptor_id=context.account.id)

    if result.is_NO_BATTLE_REQUEST:
        raise utils_views.ViewError(code='pvp.accept_arena_battle.no_battle_request_found',
                                    message='Хранитель отозвал свой вызов')

    if result.is_ALREADY_IN_BATTLE:
        raise utils_views.ViewError(code='pvp.accept_arena_battle.already_in_battle',
                                    message='Хранитель уже вступил в бой')

    participants_ids.remove(context.account.id)

    supervisor_task = logic.initiate_battle(initiator_id=list(participants_ids)[0],
                                            acceptor_id=context.account.id,
                                            battle_id=battle_id)

    return utils_views.AjaxProcessing(supervisor_task.status_url)


@CanParticipateInPvPProcessor()
@utils_api.Processor(versions=(conf.settings.CREATE_ARENA_BOT_BATTLE_API_VERSION,))
@resource('api', 'create-arena-bot-battle', method='post', name='api-create-arena-bot-battle')
def create_arena_bot_battle(context):

    # Выбираем всех ботов и перебором пытаемся создать бой с каждым из них
    # В случае тормозов или нехватки ботов их надо добавить
    #
    # Плохое решение, правильным было бы реализовать отдельный метод на стороне matchmaker сервиса,
    # который сам будет выбирать бота для битвы исходя из переданного (в вызове или в конфигах или ещё как) списка.
    bots_query = accounts_prototypes.AccountPrototype._model_class.objects.filter(is_bot=True)

    bots_ids = list(bots_query.values_list('id', flat=True))

    random.shuffle(bots_ids)

    for bot_id in bots_ids:
        result, battle_id = tt_services.matchmaker.cmd_create_battle(matchmaker_type=relations.MATCHMAKER_TYPE.BOT,
                                                                     participants_ids=(context.account.id, bot_id))

        if result.is_ALREADY_IN_BATTLE:
            continue

        if not result.is_SUCCESS:
            raise utils_views.ViewError(code='pvp.create_arena_bot_battle.unknown_error',
                                        message='Неизвестная ошибка. Пожалуйста, подождите немного и повторите попытку.')

        supervisor_task = logic.initiate_battle(initiator_id=bot_id,
                                                acceptor_id=context.account.id,
                                                battle_id=battle_id)

        return utils_views.AjaxProcessing(supervisor_task.status_url)

    raise utils_views.ViewError(code='pvp.create_arena_bot_battle.no_free_bots',
                                message='Не найдено свободных противников. Пожалуйста, подождите немного и повторите попытку.')


@utils_api.Processor(versions=(conf.settings.INFO_API_VERSION,))
@resource('api', 'info', method='get', name='api-info')
def info(context):
    return utils_views.AjaxOk(content={'info': logic.arena_info()})
