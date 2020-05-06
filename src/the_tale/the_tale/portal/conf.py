
import smart_imports

smart_imports.all()


SITE_SECTIONS = ((re.compile(r'^/$'), 'index'),
                 (re.compile(r'^/search.*$'), 'search'),
                 (re.compile(r'^/chat.*$'), 'chat'),
                 (re.compile(r'^/news.*$'), 'news'),
                 (re.compile(r'^/forum.*$'), 'forum'),
                 (re.compile(r'^/chat.*$'), 'chat'),
                 (re.compile(r'^/shop.*$'), 'shop'),
                 (re.compile(r'^/linguistics.*$'), 'world'),
                 (re.compile(r'^/accounts/auth.*$'), 'auth'),
                 (re.compile(r'^/accounts/profile.*$'), 'profile'),
                 (re.compile(r'^/accounts/messages.*$'), 'personal_messages'),
                 (re.compile(r'^/accounts/.*$'), 'community'),
                 (re.compile(r'^/game/heroes.*$'), 'hero'),
                 (re.compile(r'^/game/bills.*$'), 'world'),
                 (re.compile(r'^/game/chronicle.*$'), 'world'),
                 (re.compile(r'^/game/ratings.*$'), 'community'),
                 (re.compile(r'^/game/pvp/calls.*$'), 'world'),
                 (re.compile(r'^/game/map/'), 'map'),
                 (re.compile(r'^/game/map.*$'), None),
                 (re.compile(r'^/game.*$'), 'game'),
                 (re.compile(r'^/guide.*$'), 'guide'))


settings = utils_app_settings.app_settings('PORTAL',

                                           FAQ_URL=django_reverse_lazy('forum:threads:show', args=[126]),
                                           PLAYERS_PROJECTS_URL=django_reverse_lazy('forum:subcategories:show', args=[43]),
                                           ERRORS_URL=django_reverse_lazy('forum:subcategory', args=['erros']),
                                           BILLS_ON_INDEX=7,
                                           CHRONICLE_RECORDS_ON_INDEX=10,
                                           FORUM_COMMON_THREADS_ON_INDEX=9,
                                           FORUM_CLAN_THREADS_ON_INDEX=4,
                                           FORUM_RPG_THREADS_ON_INDEX=4,
                                           FORUM_GAMES_THREADS_ON_INDEX=4,
                                           BLOG_POSTS_ON_INDEX=7,
                                           SETTINGS_ACCOUNT_OF_THE_DAY_KEY='account of the day',
                                           FIRST_EDITION_DATE=datetime.datetime(2012, 10, 29),
                                           NEWS_ON_INDEX=3,

                                           FORUM_RPG_SUBCATEGORY='forum_rpg',
                                           FORUM_GAMES_SUBCATEGORY='forum_games',

                                           PREMIUM_DAYS_FOR_HERO_OF_THE_DAY=30,

                                           ENABLE_WORKER_LONG_COMMANDS=True,

                                           SETTINGS_CDN_INFO_KEY='cdn info',

                                           TT_DISCORD_ENTRY_POINT='http://localhost:10022/',

                                           DISCORD_BIND_CODE_EXPIRE_TIMEOUT=10*60,

                                           LANDING_MOB_DESCRIPTION_MAX_LENGTH=1000)
