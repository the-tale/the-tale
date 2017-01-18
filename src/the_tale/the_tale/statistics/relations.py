# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class VALUE_TYPE(DjangoEnum):
    records = ( ('INT', 0, 'int'),
                ('FLOAT', 1, 'float') )


class RECORD_TYPE(DjangoEnum):
    value_type = Column(unique=False)
    comment = Column()

    records = ( ('TEST_INT', 0, 'тестовые данные (int)', VALUE_TYPE.INT, 'тестовые данные (int)'),
                ('TEST_FLOAT', 1, 'тестовые данные (float)', VALUE_TYPE.FLOAT, 'тестовые данные (float)'),

                ('REGISTRATIONS_COMPLETED', 10, 'завершённые регистрации в день', VALUE_TYPE.INT, 'завершённые регистрации (в день)'),
                ('REGISTRATIONS_TRIES', 11, 'попытки регистраций в день', VALUE_TYPE.INT, 'все попытки регистраций (в день)'),
                ('REGISTRATIONS_COMPLETED_PERCENTS', 12, 'процент завершённых регистрации в день', VALUE_TYPE.FLOAT, 'процент завершённх регистраций (в день)'),
                ('REGISTRATIONS_TOTAL', 13, 'всего аккаунтов', VALUE_TYPE.INT, 'всего аккаунтов'),

                ('ALIVE_AFTER_DAY', 14, 'конверсия 1-ого дня', VALUE_TYPE.INT, 'зарегистрировались и были в игре через день'),
                ('ALIVE_AFTER_WEEK', 15, 'конверсия 1-ой недели', VALUE_TYPE.INT, 'зарегистрировались и были в игре через неделю'),
                ('ALIVE_AFTER_MONTH', 16, 'конверсия 1-ого месяца', VALUE_TYPE.INT, 'зарегистрировались и были в игре через месяц'),
                ('ALIVE_AFTER_3_MONTH', 17, 'конверсия 3-ого месяца', VALUE_TYPE.INT, 'зарегистрировались и были в игре через 3 месяца'),
                ('ALIVE_AFTER_6_MONTH', 18, 'конверсия 6-ого месяца', VALUE_TYPE.INT, 'зарегистрировались и были в игре через 6 месяцев'),
                ('ALIVE_AFTER_YEAR', 19, 'конверсия 1-ого года', VALUE_TYPE.INT, 'зарегистрировались и были в игре через год'),
                ('ALIVE_AFTER_0', 20, 'всего регистраций', VALUE_TYPE.INT, 'зарегистрировались'),

                ('LIFETIME', 21, 'lifetime', VALUE_TYPE.FLOAT, 'средне время жизни игроков'),
                ('LIFETIME_PERCENT', 22, 'lifetime процент от максимума', VALUE_TYPE.FLOAT, 'процент времени жизни игроков от максимума'),

                ('REFERRALS', 23, 'рефералы в день', VALUE_TYPE.INT, 'завершённые рефералы (в день)'),
                ('REFERRALS_TOTAL', 24, 'всего рефералов', VALUE_TYPE.INT, 'всего рефералов'),
                ('REFERRALS_PERCENTS', 25, 'процент рефералов', VALUE_TYPE.INT, 'процент рефералов'),

                ('PAYERS', 26, 'количество плательщиков в день', VALUE_TYPE.INT, 'количество плательщиков за день'),
                ('INCOME', 27, 'куплено печенек в день', VALUE_TYPE.INT, 'куплено печенек за день'),
                ('ARPPU', 28, 'ARPPU в день', VALUE_TYPE.FLOAT, 'средний чек на плательщика (Average Revenue per Paying User)'),
                ('INCOME_TOTAL', 29, 'куплено печенек всего', VALUE_TYPE.INT, 'куплено печенек всего'),
                ('DAYS_BEFORE_PAYMENT', 30, 'дней до 1-ой покупки', VALUE_TYPE.FLOAT, 'дней до 1-ой покупки'),
                ('APRNU_WEEK', 31, 'APRNU за неделю', VALUE_TYPE.FLOAT, 'средний доход с нового игрока за неделю (Average Revenue per New User)'),
                ('APRNU_MONTH', 32, 'APRNU за месяц', VALUE_TYPE.FLOAT, 'средний доход с нового игрока за месяц (Average Revenue per New User)'),
                ('APRNU_3_MONTH', 33, 'APRNU за 3 месяца', VALUE_TYPE.FLOAT, 'средний доход с нового игрока за 3 месяца(Average Revenue per New User)'),
                ('LTV', 34, 'Life Time Value', VALUE_TYPE.FLOAT, 'средний доход с нового игрока за всё время'),

                ('INCOME_FROM_FORUM', 35, 'доход от форумчан', VALUE_TYPE.INT, 'доход от форумчан за последний месяц'),
                ('INCOME_FROM_SILENT', 36, 'доход от молчунов', VALUE_TYPE.INT, 'доход от молчунов за последний месяц'),
                ('INCOME_FROM_GUILD_MEMBERS', 37, 'доход от гильдейцев', VALUE_TYPE.INT, 'доход от гильдейцев за последний месяц'),
                ('INCOME_FROM_SINGLES', 38, 'доход от одиночек', VALUE_TYPE.INT, 'доход от одиночек за последний месяц'),

                ('INCOME_FROM_GOODS_PREMIUM', 39, 'доход от подписок', VALUE_TYPE.INT, 'доход от подписок за день'),
                ('INCOME_FROM_GOODS_ENERGY', 40, 'доход от энергии', VALUE_TYPE.INT, 'доход от энергии за день'),
                ('INCOME_FROM_GOODS_CHEST', 41, 'доход от сундуков', VALUE_TYPE.INT, 'доход от сундуков за день'),
                ('INCOME_FROM_GOODS_PREFERENCES', 42, 'доход от предпочтений', VALUE_TYPE.INT, 'доход от предпочтений за день'),
                ('INCOME_FROM_GOODS_PREFERENCES_RESET', 43, 'доход от сброса предпочтений', VALUE_TYPE.INT, 'доход от сброса предпочтений за день'),
                ('INCOME_FROM_GOODS_HABITS', 44, 'доход от черт', VALUE_TYPE.INT, 'доход от черт за день'),
                ('INCOME_FROM_GOODS_ABILITIES', 45, 'доход от способностей', VALUE_TYPE.INT, 'доход от способностей за день'),
                ('INCOME_FROM_GOODS_CLANS', 46, 'доход от гильдий', VALUE_TYPE.INT, 'доход от гильдий за день'),
                ('INCOME_FROM_GOODS_OTHER', 47, 'доход от остального', VALUE_TYPE.INT, 'доход от остального за день'),

                ('PREMIUMS', 48, 'количество подписчиков', VALUE_TYPE.INT, 'количество подписчиков'),
                ('PREMIUMS_PERCENTS', 49, 'процент подписчиков', VALUE_TYPE.FLOAT, 'процент подписчиков'),
                ('ACTIVE', 50, 'активных за день', VALUE_TYPE.INT, 'количество активных игроков'),
                ('DAU', 51, 'DAU', VALUE_TYPE.INT, 'DAU'),
                ('MAU', 52, 'MAU', VALUE_TYPE.INT, 'MAU'),

                ('ARPU', 53, 'ARPU в день', VALUE_TYPE.FLOAT, 'средний доход на активного игрока в день'),
                ('PU', 54, 'заплатившие хоть раз', VALUE_TYPE.FLOAT, 'заплатившие хоть раз'),
                ('PU_PERCENTS', 55, 'процент заплативших хоть раз', VALUE_TYPE.FLOAT, 'процент заплативших хоть раз'),

                ('INCOME_GROUP_0_500', 56, 'заплатило 0-500 печенек', VALUE_TYPE.INT, 'заплатило 0-500 печенек'),
                ('INCOME_GROUP_500_1000', 57, 'заплатило 500-1000 печенек', VALUE_TYPE.INT, 'заплатило 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500', 58, 'заплатило 1000-2500 печенек', VALUE_TYPE.INT, 'заплатило 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000', 59, 'заплатило 2500-10000 печенек', VALUE_TYPE.INT, 'заплатило 2500-10000 печенек'),
                ('INCOME_GROUP_10000', 60, 'заплатило >10000 печенек', VALUE_TYPE.INT, 'заплатило >10000 печенек'),

                ('INCOME_GROUP_0_500_PERCENTS', 61, '% заплатило 0-500 печенек', VALUE_TYPE.FLOAT, '% заплатило 0-500 печенек'),
                ('INCOME_GROUP_500_1000_PERCENTS', 62, '% заплатило 500-1000 печенек', VALUE_TYPE.FLOAT, '% заплатило 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500_PERCENTS', 63, '% заплатило 1000-2500 печенек', VALUE_TYPE.FLOAT, '% заплатило 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000_PERCENTS', 64, '% заплатило 2500-10000 печенек', VALUE_TYPE.FLOAT, '% заплатило 2500-10000 печенек'),
                ('INCOME_GROUP_10000_PERCENTS', 65, '% заплатило >10000 печенек', VALUE_TYPE.FLOAT, '% заплатило >10000 печенек'),

                ('INCOME_GROUP_0_500_INCOME', 66, 'от заплативших 0-500 печенек', VALUE_TYPE.INT, 'доходов от заплативших 0-500 печенек'),
                ('INCOME_GROUP_500_1000_INCOME', 67, 'от заплативших 500-1000 печенек', VALUE_TYPE.INT, 'доходов от заплативших 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500_INCOME', 68, 'от заплативших 1000-2500 печенек', VALUE_TYPE.INT, 'доходов от заплативших 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000_INCOME', 69, 'от заплативших 2500-10000 печенек', VALUE_TYPE.INT, 'доходов от заплативших 2500-10000 печенек'),
                ('INCOME_GROUP_10000_INCOME', 70, 'от заплативших >10000 печенек', VALUE_TYPE.INT, 'доходов от заплативших >10000 печенек'),

                ('INCOME_GROUP_0_500_INCOME_PERCENTS', 71, '% от заплативших 0-500 печенек', VALUE_TYPE.FLOAT, '% доходов от заплативших 0-500 печенек'),
                ('INCOME_GROUP_500_1000_INCOME_PERCENTS', 72, '% от заплативших 500-1000 печенек', VALUE_TYPE.FLOAT, '% доходов от заплативших 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500_INCOME_PERCENTS', 73, '% от заплативших 1000-2500 печенек', VALUE_TYPE.FLOAT, '% доходов от заплативших 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000_INCOME_PERCENTS', 74, '% от заплативших 2500-10000 печенек', VALUE_TYPE.FLOAT, '% доходов от заплативших 2500-10000 печенек'),
                ('INCOME_GROUP_10000_INCOME_PERCENTS', 75, '% от заплативших >10000 печенек', VALUE_TYPE.FLOAT, '% доходов от заплативших >10000 печенек'),

                ('ACTIVE_OLDER_DAY', 76, 'старше 1-ого дня', VALUE_TYPE.INT, 'активны и зарегистрировались в течение дня'),
                ('ACTIVE_OLDER_WEEK', 77, 'старше 1-ой недели', VALUE_TYPE.INT, 'активны и зарегистрировались в течение недели'),
                ('ACTIVE_OLDER_MONTH', 78, 'старше 1-ого месяца', VALUE_TYPE.INT, 'активны и зарегистрировались в течение месяца'),
                ('ACTIVE_OLDER_3_MONTH', 79, 'старше 3-ого месяца', VALUE_TYPE.INT, 'активны и зарегистрировались в течение 3 месяцев'),
                ('ACTIVE_OLDER_6_MONTH', 80, 'старше 6-ого месяца', VALUE_TYPE.INT, 'активны и зарегистрировались в течение 6 месяцев'),
                ('ACTIVE_OLDER_YEAR', 81, 'старше 1-ого года', VALUE_TYPE.INT, 'активны и зарегистрировались в течение года'),

                ('INCOME_FROM_FORUM_PERCENTS', 82, '% дохода от форумчан', VALUE_TYPE.INT, '% дохода от форумчан за последний месяц'),
                ('INCOME_FROM_SILENT_PERCENTS', 83, '% дохода от молчунов', VALUE_TYPE.INT, '% дохода от молчунов за последний месяц'),
                ('INCOME_FROM_GUILD_MEMBERS_PERCENTS', 84, '% дохода от гильдейцев', VALUE_TYPE.INT, '% дохода от гильдейцев за последний месяц'),
                ('INCOME_FROM_SINGLES_PERCENTS', 85, '% дохода от одиночек', VALUE_TYPE.INT, '% дохода от одиночек за последний месяц'),

                ('INCOME_FROM_GOODS_PREMIUM_PERCENTS', 86, '% дохода от подписок', VALUE_TYPE.INT, '% дохода от подписок за день'),
                ('INCOME_FROM_GOODS_ENERGY_PERCENTS', 87, '% дохода от энергии', VALUE_TYPE.INT, '% дохода от энергии за день'),
                ('INCOME_FROM_GOODS_CHEST_PERCENTS', 88, '% дохода от сундуков', VALUE_TYPE.INT, '% дохода от сундуков за день'),
                ('INCOME_FROM_GOODS_PREFERENCES_PERCENTS', 89, '% дохода от предпочтений', VALUE_TYPE.INT, '% дохода от предпочтений за день'),
                ('INCOME_FROM_GOODS_PREFERENCES_RESET_PERCENTS', 90, '% дохода от сброса предпочтений', VALUE_TYPE.INT, '% дохода от сброса предпочтений за день'),
                ('INCOME_FROM_GOODS_HABITS_PERCENTS', 91, '% дохода от черт', VALUE_TYPE.INT, '% дохода от черт за день'),
                ('INCOME_FROM_GOODS_ABILITIES_PERCENTS', 92, '% дохода от способностей', VALUE_TYPE.INT, '% дохода от способностей за день'),
                ('INCOME_FROM_GOODS_CLANS_PERCENTS', 93, '% дохода от гильдий', VALUE_TYPE.INT, '% дохода от гильдий за день'),
                ('INCOME_FROM_GOODS_OTHER_PERCENTS', 94, '% дохода от остального', VALUE_TYPE.INT, '% дохода от остального за день'),

                ('REVENUE', 95, 'Доход (за предыдущий месяц)', VALUE_TYPE.INT, 'доход за предыдущий месяц'),

                ('PAYERS_IN_MONTH', 96, 'количество плательщиков в месяц', VALUE_TYPE.INT, 'количество плательщиков за месяц'),
                ('INCOME_IN_MONTH', 97, 'куплено печенек в месяц', VALUE_TYPE.INT, 'куплено печенек за месяц'),
                ('ARPPU_IN_MONTH', 98, 'ARPPU в месяц', VALUE_TYPE.FLOAT, 'средний чек на плательщика за месяц'),
                ('ARPU_IN_MONTH', 99, 'ARPU в месяц', VALUE_TYPE.FLOAT, 'средний чек на активного игрока за месяц'),

                ('REGISTRATIONS_COMPLETED_IN_MONTH', 100, 'завершённые регистрации в месяц', VALUE_TYPE.INT, 'завершённые регистрации (в месяц)'),
                ('REGISTRATIONS_TRIES_IN_MONTH', 101, 'попытки регистраций в месяц', VALUE_TYPE.INT, 'все попытки регистраций (в месяц)'),
                ('REGISTRATIONS_COMPLETED_PERCENTS_IN_MONTH', 102, 'процент завершённых регистрации в месяц', VALUE_TYPE.FLOAT, 'процент завершённх регистраций (в месяц)'),

                ('REFERRALS_IN_MONTH', 103, 'рефералы в месяц', VALUE_TYPE.INT, 'завершённые рефералы (в месяц)'),

                ('INCOME_FROM_GOODS_MARKET_COMMISSION', 104, 'доход от комиссии на рынке', VALUE_TYPE.INT, 'доход от комиссии на рынке'),
                ('INCOME_FROM_GOODS_MARKET_COMMISSION_PERCENTS', 105, '% дохода от комиссии на рынке', VALUE_TYPE.INT, '% дохода от комиссии на рынке за день'),

                ('INFINIT_PREMIUMS', 106, 'количество вечных подписчиков', VALUE_TYPE.INT, 'количество вечных подписчиков'),

                ('INCOME_FROM_TRANSFER_MONEY_COMMISSION', 107, 'доход от комиссии за перечисление печенек', VALUE_TYPE.INT, 'доход от комиссии за перечисление печенек'),
                ('INCOME_FROM_TRANSFER_MONEY_COMMISSION_PERCENTS', 108, '% дохода за перечисления печенек', VALUE_TYPE.INT, '% дохода за перечисления печенек'),

                ('FORUM_POSTS', 109, 'сообщений на форуме в день', VALUE_TYPE.INT, 'сообщений на форуме в день'),
                ('FORUM_POSTS_IN_MONTH', 110, 'сообщений на форуме в месяц', VALUE_TYPE.INT, 'сообщений на форуме в месяц'),
                ('FORUM_POSTS_TOTAL', 111, 'сообщений на форуме всего', VALUE_TYPE.INT, 'сообщений на форуме всего'),
                ('FORUM_THREADS', 112, 'тем на форуме в день', VALUE_TYPE.INT, 'тем на форуме в день'),
                ('FORUM_THREADS_IN_MONTH', 113, 'тем на форуме в месяц', VALUE_TYPE.INT, 'тем на форуме в месяц'),
                ('FORUM_THREADS_TOTAL', 114, 'тем на форуме всего', VALUE_TYPE.INT, 'тем на форуме всего'),
                ('FORUM_POSTS_PER_THREAD_IN_MONTH', 115, 'сообщений на тему на форуме в месяц', VALUE_TYPE.INT, 'соообщений на тему на форуме в месяц'),

                ('BILLS', 116, 'записей в Книгу Судеб в день', VALUE_TYPE.INT, 'записей в Книгу Судеб в день'),
                ('BILLS_IN_MONTH', 117, 'записей в Книгу Судеб в месяц', VALUE_TYPE.INT, 'записей в Книгу Судеб в месяц'),
                ('BILLS_TOTAL', 118, 'записей в Книгу Судеб всего', VALUE_TYPE.INT, 'записей в Книгу Судеб всего'),
                ('BILLS_VOTES', 119, 'голосов за запись в день', VALUE_TYPE.INT, 'голосов за запись в день'),
                ('BILLS_VOTES_IN_MONTH', 120, 'голосов за запись в месяц', VALUE_TYPE.INT, 'голосов за запись в месяц'),
                ('BILLS_VOTES_TOTAL', 121, 'голосов за запись всего', VALUE_TYPE.INT, 'голосов за запись всего'),
                ('BILLS_VOTES_PER_BILL_IN_MONTH', 122, 'голосов на закон в месяц', VALUE_TYPE.INT, 'голосов на закон в месяц'),

                ('FOLCLOR_POSTS', 123, 'произведений фольклора в день', VALUE_TYPE.INT, 'произведений фольклора в день'),
                ('FOLCLOR_POSTS_IN_MONTH', 124, 'произведений фольклора в месяц', VALUE_TYPE.INT, 'произведений фольклора в месяц'),
                ('FOLCLOR_POSTS_TOTAL', 125, 'произведений фольклора всего', VALUE_TYPE.INT, 'фольклора всего'),
                ('FOLCLOR_VOTES', 126, 'голосов за произведение в день', VALUE_TYPE.INT, 'голосов за произведение в день'),
                ('FOLCLOR_VOTES_IN_MONTH', 127, 'голосов за произведение в месяц', VALUE_TYPE.INT, 'голосов за произведение в месяц'),
                ('FOLCLOR_VOTES_TOTAL', 128, 'голосов за произведение всего', VALUE_TYPE.INT, 'голосов за произведение всего'),
                ('FOLCLOR_VOTES_PER_POST_IN_MONTH', 129, 'голосов на произведение в месяц', VALUE_TYPE.INT, 'голосов на произведение в месяц'),
              )
