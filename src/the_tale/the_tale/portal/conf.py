
import smart_imports

smart_imports.all()


SITE_SECTIONS = ((re.compile(r'^/$'), 'index'),
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


settings = dext_app_settings.app_settings('PORTAL',
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

                                          FIRST_TIME_LANDING_URLS=['/landing?action=first-time-visit'],

                                          SETTINGS_PREV_CLEANING_RUN_TIME_KEY='prev cleaning run time',
                                          CLEANING_RUN_TIME=2,  # UTC time

                                          SETTINGS_PREV_STATISTICS_RUN_TIME_KEY='prev statistics run time',
                                          STATISTICS_RUN_TIME=1,  # UTC time

                                          SETTINGS_PREV_RATINGS_SYNC_TIME_KEY='prev ratings sync run time',
                                          RATINGS_SYNC_DELAY=4 * 60 * 60,

                                          SETTINGS_PREV_MIGHT_SYNC_TIME_KEY='prev might sync run time',
                                          MIGHT_SYNC_DELAY=24 * 60 * 60,

                                          SETTINGS_PREV_EXPIRE_ACCESS_TOKENS_SYNC_TIME_KEY='prev expire access tokens sync run time',
                                          EXPIRE_ACCESS_TOKENS_SYNC_DELAY=1 * 60 * 60,

                                          SETTINGS_PREV_CLEAN_REMOVED_TEMPLATES_KEY='prev clean removed templates',
                                          EXPIRE_CLEAN_REMOVED_TEMPLATES=24 * 60 * 60,

                                          SETTINGS_PREV_CDN_SYNC_TIME_KEY='prev cdn sync run time',
                                          CDN_SYNC_DELAY=5 * 60,

                                          PREMIUM_DAYS_FOR_HERO_OF_THE_DAY=30,

                                          SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY='prev real day started',
                                          REAL_DAY_STARTED_TIME=8,  # UTC hourse

                                          ENABLE_WORKER_LONG_COMMANDS=True,

                                          SETTINGS_CDN_INFO_KEY='cdn info',

                                          LANDING_MOB_DESCRIPTION_MAX_LENGTH=1000)
