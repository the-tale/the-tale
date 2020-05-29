import smart_imports

smart_imports.all()


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='portal')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())


########################################
# views
########################################

@resource('')
def index(context):
    news = news_logic.load_news_from_query(news_models.News.objects.all().order_by('-created_at')[:conf.settings.NEWS_ON_INDEX])

    account_of_the_day_id = global_settings.get(conf.settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY)

    hero_of_the_day = None
    account_of_the_day = None
    clan_of_the_day = None

    if account_of_the_day_id is not None:
        hero_of_the_day = heroes_logic.load_hero(account_id=account_of_the_day_id)
        account_of_the_day = accounts_prototypes.AccountPrototype.get_by_id(account_of_the_day_id)

        if account_of_the_day and account_of_the_day.clan_id is not None:
            clan_of_the_day = clans_logic.load_clan(clan_id=account_of_the_day.clan_id)

    forum_common_block = events_bloks.forum_common(limit=conf.settings.FORUM_COMMON_THREADS_ON_INDEX,
                                                   exclude_subcategories=(conf.settings.FORUM_RPG_SUBCATEGORY,
                                                                          conf.settings.FORUM_GAMES_SUBCATEGORY))
    forum_clan_block = None

    if context.account.is_authenticated and context.account.clan:
        clan_forum_subcategory = forum_prototypes.SubCategoryPrototype.get_by_id(context.account.clan.forum_subcategory_id)
        forum_clan_block = events_bloks.forum_subcategory('Ваша гильдия',
                                                          subcategory=clan_forum_subcategory,
                                                          limit=conf.settings.FORUM_CLAN_THREADS_ON_INDEX)

    forum_rpg_subcategory = forum_prototypes.SubCategoryPrototype.get_by_uid(conf.settings.FORUM_RPG_SUBCATEGORY)
    forum_rpg_block = events_bloks.forum_subcategory('Ролевые Игры',
                                                     subcategory=forum_rpg_subcategory,
                                                     limit=conf.settings.FORUM_RPG_THREADS_ON_INDEX)

    forum_games_subcategory = forum_prototypes.SubCategoryPrototype.get_by_uid(conf.settings.FORUM_GAMES_SUBCATEGORY)
    forum_games_block = events_bloks.forum_subcategory('Форумные Игры',
                                                       subcategory=forum_games_subcategory,
                                                       limit=conf.settings.FORUM_GAMES_THREADS_ON_INDEX)

    folclor_block = events_bloks.blogs_common(limit=conf.settings.BLOG_POSTS_ON_INDEX)

    bills_block = events_bloks.bills_common(limit=conf.settings.BILLS_ON_INDEX)

    map_info = map_storage.map_info.item

    total_events, events = chronicle_tt_services.chronicle.cmd_get_last_events(tags=(), number=conf.settings.CHRONICLE_RECORDS_ON_INDEX)

    tt_api_events_log.fill_events_wtih_meta_objects(events)

    return utils_views.Page('portal/index.html',
                            content={'resource': context.resource,
                                     'news': news,
                                     'forum_common_block': forum_common_block,
                                     'forum_clan_block': forum_clan_block,
                                     'forum_rpg_block': forum_rpg_block,
                                     'forum_games_block': forum_games_block,
                                     'folclor_block': folclor_block,
                                     'bills_block': bills_block,
                                     'hero_of_the_day': hero_of_the_day,
                                     'account_of_the_day': account_of_the_day,
                                     'clan_of_the_day': clan_of_the_day,
                                     'map_info': map_info,
                                     'TERRAIN': map_relations.TERRAIN,
                                     'MAP_STATISTICS': map_relations.MAP_STATISTICS,
                                     'chronicle_records': events,
                                     'RACE': game_relations.RACE,
                                     'first_time_visit': accounts_logic.is_first_time_visit(context.django_request)})


@resource('search')
def search(context):
    return utils_views.Page('portal/search.html',
                            content={'resource': context.resource})


@resource('chat')
def chat(context):
    return utils_views.Page('portal/chat.html',
                            content={'resource': context.resource})


@accounts_views.LoginRequiredProcessor(error_message='Вы должны войти в игру, чтобы связать свой аккаунт с аккаунтом Discord')
@accounts_views.FullAccountProcessor()
@resource('chat-bind-discord')
def chat_bind_discord(context):

    bind_code = tt_services.discord.cmd_get_bind_code(user=discord.construct_user_info(context.account),
                                                      expire_timeout=conf.settings.DISCORD_BIND_CODE_EXPIRE_TIMEOUT)

    return utils_views.Page('portal/bind_discord_dialog.html',
                            content={'resource': context.resource,
                                     'bind_code': bind_code,
                                     'expire_timeout': conf.settings.DISCORD_BIND_CODE_EXPIRE_TIMEOUT})


@resource('csrf')
def handlerCSRF(context):
    raise utils_views.ViewError(code='common.csrf',
                                message=f'Неверный csrf токен. Если Вы обычный игрок, возможно, Вы случайно разлогинились — обновите страницу и снова войдите в игру. Если Вы разработчик, проверьте формирование своего запроса. [{context.django_request.GET.get("reason")}]',
                                http_status=403)


@resource('403')
def handler403(context):
    raise utils_views.ViewError(code='common.403',
                                message='Вы не имеете прав для проведение этой операции.',
                                http_status=403)


@resource('404')
def handler404(context):
    raise utils_views.ViewError(code='common.404',
                                message='Извините, запрашиваемая Вами страница не найдена.',
                                http_status=404)


@resource('500')
def handler500(context):
    raise utils_views.ViewError(code='common.500',
                                message='Извините, произошла ошибка, мы работаем над её устранением. Пожалуйста, повторите попытку позже.')


@resource('preview', method='post')
def preview(context):
    return utils_views.String(bbcode_renderers.default.render(context.django_request.POST.get('text', '')))


@utils_api.Processor(versions=('1.0',))
@resource('api', 'info', name='api-info')
def api_info(context):
    cdn_paths = logic.cdn_paths()

    return utils_views.AjaxOk(content={'static_content': cdn_paths['STATIC_CONTENT'],
                                       'game_version': django_settings.META_CONFIG.version,
                                       'turn_delta': c.TURN_DELTA,
                                       'account_id': context.account.id if context.account.is_authenticated else None,
                                       'account_name': context.account.nick if context.account.is_authenticated else None,
                                       'abilities_cost': {ability_type.value: ability_type.cost for ability_type in abilities_relations.ABILITY_TYPE.records}})
