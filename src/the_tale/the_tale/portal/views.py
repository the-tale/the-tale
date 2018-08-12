import smart_imports

smart_imports.all()


class PortalResource(utils_resources.Resource):

    @dext_old_views.handler('', method='get')
    def index(self):

        if conf.settings.ENABLE_FIRST_TIME_REDIRECT and accounts_logic.is_first_time_visit(self.request):
            return self.redirect(random.choice(conf.settings.FIRST_TIME_LANDING_URLS))

        news = news_logic.load_news_from_query(news_models.News.objects.all().order_by('-created_at')[:conf.settings.NEWS_ON_INDEX])

        account_of_the_day_id = dext_settings.settings.get(conf.settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY)

        hero_of_the_day = None
        account_of_the_day = None
        clan_of_the_day = None

        if account_of_the_day_id is not None:
            hero_of_the_day = heroes_logic.load_hero(account_id=account_of_the_day_id)
            account_of_the_day = accounts_prototypes.AccountPrototype.get_by_id(account_of_the_day_id)

            if account_of_the_day and account_of_the_day.clan_id is not None:
                clan_of_the_day = clans_prototypes.ClanPrototype.get_by_id(account_of_the_day.clan_id)

        forum_common_block = events_bloks.forum_common(limit=conf.settings.FORUM_COMMON_THREADS_ON_INDEX,
                                                       exclude_subcategories=(conf.settings.FORUM_RPG_SUBCATEGORY,
                                                                              conf.settings.FORUM_GAMES_SUBCATEGORY))
        forum_clan_block = None

        if self.account.is_authenticated and self.account.clan:
            forum_clan_block = events_bloks.forum_subcategory('Ваша гильдия',
                                                              subcategory=self.account.clan.forum_subcategory,
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

        chronicle_records = chronicle_prototypes.RecordPrototype.get_last_records(conf.settings.CHRONICLE_RECORDS_ON_INDEX)

        return self.template('portal/index.html',
                             {'news': news,
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
                              'chronicle_records': chronicle_records,
                              'RACE': game_relations.RACE})

    @dext_old_views.handler('search')
    def search(self):
        return self.template('portal/search.html', {})

    @dext_old_views.handler('landing')
    def landing(self, type="normal"):

        if self.account.is_authenticated:
            return self.redirect(dext_urls.url('portal:'))

        mobs = [mob
                for mob in mobs_storage.mobs.get_all_mobs_for_level(level=666)
                if len(mob.description) < conf.settings.LANDING_MOB_DESCRIPTION_MAX_LENGTH]

        return self.template('portal/landing.html',
                             {'current_map_version': map_storage.map_info.version,
                              'landing_type': type,
                              'mob': random.choice(mobs)})

    @dext_old_views.handler('csrf')
    def handlerCSRF(self, reason=''):
        return self.auto_error('common.csrf',
                               'Неверный csrf токен. Если Вы обычный игрок, возможно, Вы случайно разлогинились — обновите страницу и снова войдите в игру. Если Вы разработчик, проверьте формирование своего запроса. [%s]' % reason,
                               status_code=403)

    @dext_old_views.handler('403')
    def handler403(self):
        return self.auto_error('common.403',
                               'Вы не имеете прав для проведение этой операции.',
                               status_code=403)

    @dext_old_views.handler('404')
    def handler404(self):
        return self.auto_error('common.404',
                               'Извините, запрашиваемая Вами страница не найдена.',
                               status_code=404)

    @dext_old_views.handler('500')
    def handler500(self):
        return self.auto_error('common.500',
                               'Извините, произошла ошибка, мы работаем над её устранением. Пожалуйста, повторите попытку позже.')

    @dext_old_views.handler('preview', name='preview', method='post')
    def preview(self):
        return self.string(utils_bbcode.render(self.request.POST.get('text', '')))

    @utils_api.handler(versions=('1.0',))
    @dext_old_views.handler('api', 'info', name='api-info', method='get')
    def api_info(self, api_version):
        cdn_paths = logic.cdn_paths()

        return self.ok(data={'static_content': cdn_paths['STATIC_CONTENT'],
                             'game_version': django_settings.META_CONFIG.version,
                             'turn_delta': c.TURN_DELTA,
                             'account_id': self.account.id if self.account.is_authenticated else None,
                             'account_name': self.account.nick if self.account.is_authenticated else None,
                             'abilities_cost': {ability_type.value: ability_type.cost for ability_type in abilities_relations.ABILITY_TYPE.records}})
