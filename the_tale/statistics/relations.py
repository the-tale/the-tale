# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class VALUE_TYPE(DjangoEnum):
    records = ( ('INT', 0, u'int'),
                ('FLOAT', 1, u'float') )


class RECORD_TYPE(DjangoEnum):
    value_type = Column(unique=False)
    comment = Column()

    records = ( ('TEST_INT', 0, u'тестовые данные (int)', VALUE_TYPE.INT, u'тестовые данные (int)'),
                ('TEST_FLOAT', 1, u'тестовые данные (float)', VALUE_TYPE.FLOAT, u'тестовые данные (float)'),

                ('REGISTRATIONS_COMPLETED', 10, u'завершённые регистрации в день', VALUE_TYPE.INT, u'завершённые регистрации (в день)'),
                ('REGISTRATIONS_TRIES', 11, u'попытки регистраций в день', VALUE_TYPE.INT, u'все попытки регистраций (в день)'),
                ('REGISTRATIONS_COMPLETED_PERCENTS', 12, u'процент завершённых регистрации в день', VALUE_TYPE.FLOAT, u'процент завершённх регистраций (в день)'),
                ('REGISTRATIONS_TOTAL', 13, u'всего аккаунтов', VALUE_TYPE.INT, u'всего аккаунтов'),

                ('ALIVE_AFTER_DAY', 14, u'конверсия 1-ого дня', VALUE_TYPE.INT, u'зарегистрировались и были в игре через день'),
                ('ALIVE_AFTER_WEEK', 15, u'конверсия 1-ой недели', VALUE_TYPE.INT, u'зарегистрировались и были в игре через неделю'),
                ('ALIVE_AFTER_MONTH', 16, u'конверсия 1-ого месяца', VALUE_TYPE.INT, u'зарегистрировались и были в игре через месяц'),
                ('ALIVE_AFTER_3_MONTH', 17, u'конверсия 3-ого месяца', VALUE_TYPE.INT, u'зарегистрировались и были в игре через 3 месяца'),
                ('ALIVE_AFTER_6_MONTH', 18, u'конверсия 6-ого месяца', VALUE_TYPE.INT, u'зарегистрировались и были в игре через 6 месяцев'),
                ('ALIVE_AFTER_YEAR', 19, u'конверсия 1-ого года', VALUE_TYPE.INT, u'зарегистрировались и были в игре через год'),
                ('ALIVE_AFTER_0', 20, u'всего регистраций', VALUE_TYPE.INT, u'зарегистрировались'),

                ('LIFETIME', 21, u'lifetime', VALUE_TYPE.FLOAT, u'средне время жизни игроков, зарегистрировавшихся в течении недели'),
                ('LIFETIME_PERCENT', 22, u'lifetime процент от максимума', VALUE_TYPE.FLOAT, u'процент времени жизни игроков, зарегистрировавшихся в течении недели, от максимума'),

                ('REFERRALS', 23, u'рефералы в день', VALUE_TYPE.INT, u'завершённые рефералы (в день)'),
                ('REFERRALS_TOTAL', 24, u'всего рефералов', VALUE_TYPE.INT, u'всего рефералов'),
                ('REFERRALS_PERCENTS', 25, u'процент рефералов', VALUE_TYPE.INT, u'процент рефералов'),

                ('PAYERS', 26, u'количество плательщиков в день', VALUE_TYPE.INT, u'количество плательщиков за день'),
                ('INCOME', 27, u'куплено печенек в день', VALUE_TYPE.INT, u'куплено печенек за день'),
                ('ARPPU', 28, u'ARPPU в день', VALUE_TYPE.FLOAT, u'средний чек на плательщика (Average Revenue per Paying User)'),
                ('INCOME_TOTAL', 29, u'куплено печенек всего', VALUE_TYPE.INT, u'куплено печенек всего'),
                ('DAYS_BEFORE_PAYMENT', 30, u'дней до 1-ой покупки', VALUE_TYPE.FLOAT, u'дней до 1-ой покупки'),
                ('APRNU_WEEK', 31, u'APRNU за неделю', VALUE_TYPE.FLOAT, u'средний доход с нового игрока за неделю (Average Revenue per New User)'),
                ('APRNU_MONTH', 32, u'APRNU за месяц', VALUE_TYPE.FLOAT, u'средний доход с нового игрока за месяц (Average Revenue per New User)'),
                ('APRNU_3_MONTH', 33, u'APRNU за 3 месяца', VALUE_TYPE.FLOAT, u'средний доход с нового игрока за 3 месяца(Average Revenue per New User)'),
                ('LTV', 34, u'Life Time Value', VALUE_TYPE.FLOAT, u'средний доход с нового игрока за всё время'),

                ('INCOME_FROM_FORUM', 35, u'доход от форумчан', VALUE_TYPE.INT, u'доход от форумчан за последний месяц'),
                ('INCOME_FROM_SILENT', 36, u'доход от молчунов', VALUE_TYPE.INT, u'доход от молчунов за последний месяц'),
                ('INCOME_FROM_GUILD_MEMBERS', 37, u'доход от гильдейцев', VALUE_TYPE.INT, u'доход от гильдейцев за последний месяц'),
                ('INCOME_FROM_SINGLES', 38, u'доход от одиночек', VALUE_TYPE.INT, u'доход от одиночек за последний месяц'),

                ('INCOME_FROM_GOODS_PREMIUM', 39, u'доход от подписок', VALUE_TYPE.INT, u'доход от подписок за день'),
                ('INCOME_FROM_GOODS_ENERGY', 40, u'доход от энергии', VALUE_TYPE.INT, u'доход от энергии за день'),
                ('INCOME_FROM_GOODS_CHEST', 41, u'доход от сундуков', VALUE_TYPE.INT, u'доход от сундуков за день'),
                ('INCOME_FROM_GOODS_PREFERENCES', 42, u'доход от предпочтений', VALUE_TYPE.INT, u'доход от предпочтений за день'),
                ('INCOME_FROM_GOODS_PREFERENCES_RESET', 43, u'доход от сброса предпочтений', VALUE_TYPE.INT, u'доход от сброса предпочтений за день'),
                ('INCOME_FROM_GOODS_HABITS', 44, u'доход от черт', VALUE_TYPE.INT, u'доход от черт за день'),
                ('INCOME_FROM_GOODS_ABILITIES', 45, u'доход от способностей', VALUE_TYPE.INT, u'доход от способностей за день'),
                ('INCOME_FROM_GOODS_CLANS', 46, u'доход от гильдий', VALUE_TYPE.INT, u'доход от гильдий за день'),
                ('INCOME_FROM_GOODS_OTHER', 47, u'доход от остального', VALUE_TYPE.INT, u'доход от остального за день'),

                ('PREMIUMS', 48, u'количество подписчиков', VALUE_TYPE.INT, u'количество подписчиков'),
                ('PREMIUMS_PERCENTS', 49, u'процент подписчиков', VALUE_TYPE.FLOAT, u'процент подписчиков'),
                ('ACTIVE', 50, u'активных за день', VALUE_TYPE.INT, u'количество активных игроков'),
                ('DAU', 51, u'DAU', VALUE_TYPE.INT, u'DAU'),
                ('MAU', 52, u'MAU', VALUE_TYPE.INT, u'MAU'),

                ('ARPU', 53, u'ARPU в день', VALUE_TYPE.FLOAT, u'средний доход на активного игрока в день'),
                ('PU', 54, u'заплатившие хоть раз', VALUE_TYPE.FLOAT, u'заплатившие хоть раз'),
                ('PU_PERCENTS', 55, u'процент заплативших хоть раз', VALUE_TYPE.FLOAT, u'процент заплативших хоть раз'),

                ('INCOME_GROUP_0_500', 56, u'заплатило 0-500 печенек', VALUE_TYPE.INT, u'заплатило 0-500 печенек'),
                ('INCOME_GROUP_500_1000', 57, u'заплатило 500-1000 печенек', VALUE_TYPE.INT, u'заплатило 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500', 58, u'заплатило 1000-2500 печенек', VALUE_TYPE.INT, u'заплатило 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000', 59, u'заплатило 2500-10000 печенек', VALUE_TYPE.INT, u'заплатило 2500-10000 печенек'),
                ('INCOME_GROUP_10000', 60, u'заплатило >10000 печенек', VALUE_TYPE.INT, u'заплатило >10000 печенек'),

                ('INCOME_GROUP_0_500_PERCENTS', 61, u'% заплатило 0-500 печенек', VALUE_TYPE.FLOAT, u'% заплатило 0-500 печенек'),
                ('INCOME_GROUP_500_1000_PERCENTS', 62, u'% заплатило 500-1000 печенек', VALUE_TYPE.FLOAT, u'% заплатило 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500_PERCENTS', 63, u'% заплатило 1000-2500 печенек', VALUE_TYPE.FLOAT, u'% заплатило 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000_PERCENTS', 64, u'% заплатило 2500-10000 печенек', VALUE_TYPE.FLOAT, u'% заплатило 2500-10000 печенек'),
                ('INCOME_GROUP_10000_PERCENTS', 65, u'% заплатило >10000 печенек', VALUE_TYPE.FLOAT, u'% заплатило >10000 печенек'),

                ('INCOME_GROUP_0_500_INCOME', 66, u'от заплативших 0-500 печенек', VALUE_TYPE.INT, u'доходов от заплативших 0-500 печенек'),
                ('INCOME_GROUP_500_1000_INCOME', 67, u'от заплативших 500-1000 печенек', VALUE_TYPE.INT, u'доходов от заплативших 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500_INCOME', 68, u'от заплативших 1000-2500 печенек', VALUE_TYPE.INT, u'доходов от заплативших 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000_INCOME', 69, u'от заплативших 2500-10000 печенек', VALUE_TYPE.INT, u'доходов от заплативших 2500-10000 печенек'),
                ('INCOME_GROUP_10000_INCOME', 70, u'от заплативших >10000 печенек', VALUE_TYPE.INT, u'доходов от заплативших >10000 печенек'),

                ('INCOME_GROUP_0_500_INCOME_PERCENTS', 71, u'% от заплативших 0-500 печенек', VALUE_TYPE.FLOAT, u'% доходов от заплативших 0-500 печенек'),
                ('INCOME_GROUP_500_1000_INCOME_PERCENTS', 72, u'% от заплативших 500-1000 печенек', VALUE_TYPE.FLOAT, u'% доходов от заплативших 500-1000 печенек'),
                ('INCOME_GROUP_1000_2500_INCOME_PERCENTS', 73, u'% от заплативших 1000-2500 печенек', VALUE_TYPE.FLOAT, u'% доходов от заплативших 1000-2500 печенек'),
                ('INCOME_GROUP_2500_10000_INCOME_PERCENTS', 74, u'% от заплативших 2500-10000 печенек', VALUE_TYPE.FLOAT, u'% доходов от заплативших 2500-10000 печенек'),
                ('INCOME_GROUP_10000_INCOME_PERCENTS', 75, u'% от заплативших >10000 печенек', VALUE_TYPE.FLOAT, u'% доходов от заплативших >10000 печенек'),

                ('ACTIVE_OLDER_DAY', 76, u'старше 1-ого дня', VALUE_TYPE.INT, u'активны и зарегистрировались в течение дня'),
                ('ACTIVE_OLDER_WEEK', 77, u'старше 1-ой недели', VALUE_TYPE.INT, u'активны и зарегистрировались в течение недели'),
                ('ACTIVE_OLDER_MONTH', 78, u'старше 1-ого месяца', VALUE_TYPE.INT, u'активны и зарегистрировались в течение месяца'),
                ('ACTIVE_OLDER_3_MONTH', 79, u'старше 3-ого месяца', VALUE_TYPE.INT, u'активны и зарегистрировались в течение 3 месяцев'),
                ('ACTIVE_OLDER_6_MONTH', 80, u'старше 6-ого месяца', VALUE_TYPE.INT, u'активны и зарегистрировались в течение 6 месяцев'),
                ('ACTIVE_OLDER_YEAR', 81, u'старше 1-ого года', VALUE_TYPE.INT, u'активны и зарегистрировались в течение года'),

                ('INCOME_FROM_FORUM_PERCENTS', 82, u'% дохода от форумчан', VALUE_TYPE.INT, u'% дохода от форумчан за последний месяц'),
                ('INCOME_FROM_SILENT_PERCENTS', 83, u'% дохода от молчунов', VALUE_TYPE.INT, u'% дохода от молчунов за последний месяц'),
                ('INCOME_FROM_GUILD_MEMBERS_PERCENTS', 84, u'% дохода от гильдейцев', VALUE_TYPE.INT, u'% дохода от гильдейцев за последний месяц'),
                ('INCOME_FROM_SINGLES_PERCENTS', 85, u'% дохода от одиночек', VALUE_TYPE.INT, u'% дохода от одиночек за последний месяц'),

                ('INCOME_FROM_GOODS_PREMIUM_PERCENTS', 86, u'% дохода от подписок', VALUE_TYPE.INT, u'% дохода от подписок за день'),
                ('INCOME_FROM_GOODS_ENERGY_PERCENTS', 87, u'% дохода от энергии', VALUE_TYPE.INT, u'% дохода от энергии за день'),
                ('INCOME_FROM_GOODS_CHEST_PERCENTS', 88, u'% дохода от сундуков', VALUE_TYPE.INT, u'% дохода от сундуков за день'),
                ('INCOME_FROM_GOODS_PREFERENCES_PERCENTS', 89, u'% дохода от предпочтений', VALUE_TYPE.INT, u'% дохода от предпочтений за день'),
                ('INCOME_FROM_GOODS_PREFERENCES_RESET_PERCENTS', 90, u'% дохода от сброса предпочтений', VALUE_TYPE.INT, u'% дохода от сброса предпочтений за день'),
                ('INCOME_FROM_GOODS_HABITS_PERCENTS', 91, u'% дохода от черт', VALUE_TYPE.INT, u'% дохода от черт за день'),
                ('INCOME_FROM_GOODS_ABILITIES_PERCENTS', 92, u'% дохода от способностей', VALUE_TYPE.INT, u'% дохода от способностей за день'),
                ('INCOME_FROM_GOODS_CLANS_PERCENTS', 93, u'% дохода от гильдий', VALUE_TYPE.INT, u'% дохода от гильдий за день'),
                ('INCOME_FROM_GOODS_OTHER_PERCENTS', 94, u'% дохода от остального', VALUE_TYPE.INT, u'% дохода от остального за день'),

                ('REVENUE', 95, u'Доход (за предыдущую неделю)', VALUE_TYPE.INT, u'доход за предыдущую неделю'),

                ('PAYERS_IN_MONTH', 96, u'количество плательщиков в месяц', VALUE_TYPE.INT, u'количество плательщиков за месяц'),
                ('INCOME_IN_MONTH', 97, u'куплено печенек в месяц', VALUE_TYPE.INT, u'куплено печенек за месяц'),
                ('ARPPU_IN_MONTH', 98, u'ARPPU в месяц', VALUE_TYPE.FLOAT, u'средний чек на плательщика за месяц'),
                ('ARPU_IN_MONTH', 99, u'ARPU в месяц', VALUE_TYPE.FLOAT, u'средний чек на активного игрока за месяц'),

                ('REGISTRATIONS_COMPLETED_IN_MONTH', 100, u'завершённые регистрации в месяц', VALUE_TYPE.INT, u'завершённые регистрации (в месяц)'),
                ('REGISTRATIONS_TRIES_IN_MONTH', 101, u'попытки регистраций в месяц', VALUE_TYPE.INT, u'все попытки регистраций (в месяц)'),
                ('REGISTRATIONS_COMPLETED_PERCENTS_IN_MONTH', 102, u'процент завершённых регистрации в месяц', VALUE_TYPE.FLOAT, u'процент завершённх регистраций (в месяц)'),

                ('REFERRALS_IN_MONTH', 103, u'рефералы в месяц', VALUE_TYPE.INT, u'завершённые рефералы (в месяц)'),
        )
