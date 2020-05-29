
import smart_imports

smart_imports.all()


APP_DIR = os.path.abspath(os.path.dirname(__file__))


settings = utils_app_settings.app_settings('ACCOUNTS',
                                           SESSION_REGISTRATION_REFERER_KEY='accounts_registration_referer_key',
                                           SESSION_REGISTRATION_REFERRAL_KEY='accounts_registration_referral_key',
                                           SESSION_REGISTRATION_ACTION_KEY='accounts_registration_action_key',

                                           SESSION_FIRST_TIME_VISIT_VISITED_KEY='first_time_visite_visited',
                                           SESSION_FIRST_TIME_VISIT_KEY='first_time_visite',

                                           SESSION_REMEMBER_TIME=365 * 24 * 60 * 60,

                                           REFERRAL_URL_ARGUMENT='referral',
                                           ACTION_URL_ARGUMENT='action',

                                           FORUM_COMPLAINT_THEME='/forum/threads/1177',


                                           FAST_REGISTRATION_USER_PASSWORD='password-FOR_fast-USERS',
                                           FAST_ACCOUNT_EXPIRED_TIME=3 * 24 * 60 * 60,
                                           REGISTRATION_TIMEOUT=1 * 60,
                                           RESET_PASSWORD_LENGTH=8,
                                           RESET_PASSWORD_TASK_LIVE_TIME=60 * 60,
                                           CHANGE_EMAIL_TIMEOUT=2 * 24 * 60 * 60,
                                           ACTIVE_STATE_TIMEOUT=3 * 24 * 60 * 60,
                                           ACTIVE_STATE_REFRESH_PERIOD=3 * 60 * 60,
                                           SYSTEM_USER_NICK='Смотритель',
                                           DEVELOPERS_IDS=[1, 1022],
                                           MODERATORS_IDS=[8157],

                                           ACCOUNTS_ON_PAGE=25,

                                           SHOW_SUBSCRIPTION_OFFER_AFTER=7 * 24 * 60 * 60,

                                           PREMIUM_EXPIRED_NOTIFICATION_IN=datetime.timedelta(days=3),
                                           PREMIUM_INFINIT_TIMEOUT=datetime.timedelta(days=100 * 365),

                                           INFORMER_SHOW=True,
                                           INFORMER_LINK='https://informer.the-tale.org/?id=%(account_id)d&type=4',
                                           INFORMER_CREATOR_ID=2557,
                                           INFORMER_CREATOR_NAME='Yashko',
                                           INFORMER_WIDTH=400,
                                           INFORMER_HEIGHT=50,
                                           INFORMER_FORUM_THREAD=515,

                                           INFORMER_2_CREATOR_ID=6901,
                                           INFORMER_2_CREATOR_NAME='Нико д`Лас',
                                           INFORMER_2_FORUM_THREAD=4422,

                                           NICK_REGEX=r'^[a-zA-Z0-9\-\ _а-яА-Я]+$',
                                           NICK_MIN_LENGTH=3,
                                           NICK_MAX_LENGTH=30,

                                           RESET_NICK_PREFIX='имя игрока сброшено',

                                           BOT_EMAIL_TEMPLATE='bot_%d@the-tale.org',
                                           BOT_PASSWORD='password-Bots',
                                           BOT_NICK_TEMPLATE='Существо №%d',
                                           BOT_HERO_NAME_FORMS=['Существо', 'Существа', 'Существу', 'Существо', 'Существом', 'Существе',
                                                                'Существа', 'Существ', 'Существам', 'Существ', 'Существами', 'Существах'],
                                           BOT_HERO_NAME_PROPERTIES=('ср', ),

                                           MAX_ACCOUNT_DESCRIPTION_LENGTH=10000,

                                           MINIMUM_SEND_MONEY=10,
                                           MONEY_SEND_COMMISSION=0.05,
                                           COMMISION_TRANSACTION_UID='transfer-money-between-accounts-commission',

                                           LORE_GOBLINS='https://the-tale.org/folklore/posts/506',
                                           LORE_ELFS='https://the-tale.org/folklore/posts/503',
                                           LORE_ORCS='https://the-tale.org/folklore/posts/504',
                                           LORE_DWARFS='https://the-tale.org/folklore/posts/505',
                                           LORE_HUMANS='https://the-tale.org/folklore/posts/502',

                                           GUIDE_HABITS='https://the-tale.org/guide/hero-habits',

                                           TT_PLAYERS_TIMERS_ENTRY_POINT='http://localhost:10006/',
                                           TT_PLAYERS_PROPERTIES_ENTRY_POINT='http://localhost:10014/',
                                           TT_DATA_PROTECTOR_ENTRY_POINT='http://localhost:10023/',

                                           FREE_CARDS_FOR_REGISTRATION=10)
