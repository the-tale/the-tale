# coding: utf-8

from the_tale.statistics import relations


class Plot(object):

    def __init__(self, type, y_axis):
        self.type = type
        self.y_axis = y_axis



class PlotsGroup(object):

    def __init__(self, uid, title, y_label, y2_label, plots, x_label=u'дата', y_value_range=None, y2_value_range=None, fill_graph=True, roll_period=1):
        self.uid = uid
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.y2_label = y2_label
        self.plots = plots
        self.y_value_range = y_value_range
        self.y2_value_range = y2_value_range
        self.fill_graph = fill_graph
        self.roll_period = roll_period



PLOTS_GROUPS = [
    PlotsGroup(uid='total',
               title=u'Общее количество аккаунтов',
               y_label=u'',
               y2_label=u'всего аккаунтов',
               plots=[Plot(relations.RECORD_TYPE.REGISTRATIONS_TOTAL, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.REFERRALS_TOTAL, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.PREMIUMS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INFINIT_PREMIUMS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.DAU, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.MAU, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.PU, y_axis='y2')]
               ),
    PlotsGroup(uid='total-percents',
               title=u'Общее количество аккаунтов (проценты)',
               y_label=u'',
               y2_label=u'проценты',
               y_value_range=[0, 100],
               y2_value_range=[0, 100],
               plots=[Plot(relations.RECORD_TYPE.REFERRALS_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.PREMIUMS_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.PU_PERCENTS, y_axis='y2')]
               ),
    PlotsGroup(uid='registrations',
               title=u'Регистрации',
               y_label=u'количество регистраций в день',
               y2_label=u'количество регистраций в месяц',
               plots=[Plot(relations.RECORD_TYPE.REGISTRATIONS_COMPLETED, y_axis='y1'),
                      Plot(relations.RECORD_TYPE.REGISTRATIONS_TRIES, y_axis='y1'),
                      Plot(relations.RECORD_TYPE.REFERRALS, y_axis='y1'),
                      Plot(relations.RECORD_TYPE.REGISTRATIONS_COMPLETED_IN_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.REGISTRATIONS_TRIES_IN_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.REFERRALS_IN_MONTH, y_axis='y2')                      ]
               ),
    PlotsGroup(uid='fast-conversion',
               title=u'Конверсия временных регистраций в завершённые',
               y_label=u'процент',
               y2_label=u'процент',
               plots=[Plot(relations.RECORD_TYPE.REGISTRATIONS_COMPLETED_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.REGISTRATIONS_COMPLETED_PERCENTS_IN_MONTH, y_axis='y2')],
               y_value_range=[0, 100],
               y2_value_range=[0, 100],
               ),

    PlotsGroup(uid='active-older',
               title=u'Активны и зарегистрировались N дней назад',
               y_label=u'',
               y2_label=u'количество аккаунтов',
               plots=[Plot(relations.RECORD_TYPE.DAU, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE_OLDER_DAY, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE_OLDER_WEEK, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE_OLDER_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE_OLDER_3_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE_OLDER_6_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ACTIVE_OLDER_YEAR, y_axis='y2')]
               ),

    PlotsGroup(uid='alive',
               title=u'Конверсии N-ого дня (зарегистрировались и появлялись в игре через N дней)',
               y_label=u'',
               y2_label=u'количество регистраций',
               plots=[Plot(relations.RECORD_TYPE.ALIVE_AFTER_0, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ALIVE_AFTER_DAY, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ALIVE_AFTER_WEEK, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ALIVE_AFTER_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ALIVE_AFTER_3_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ALIVE_AFTER_6_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ALIVE_AFTER_YEAR, y_axis='y2')]
               ),
    PlotsGroup(uid='lifetime',
               title=u'Lifetime (среднее время жизни зарегистрировавшихся игроков)',
               y_label=u'дни',
               y2_label=u'процент',
               y2_value_range=[0, 100],
               plots=[Plot(relations.RECORD_TYPE.LIFETIME, y_axis='y'),
                      Plot(relations.RECORD_TYPE.LIFETIME_PERCENT, y_axis='y2')] ),
    PlotsGroup(uid='payers',
               title=u'Платежи',
               y_label=u'количество',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.PAYERS, y_axis='y'),
                      Plot(relations.RECORD_TYPE.PAYERS_IN_MONTH, y_axis='y'),
                      Plot(relations.RECORD_TYPE.INCOME, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_IN_MONTH, y_axis='y2')] ),

    PlotsGroup(uid='total-income',
               title=u'Общий доход',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.INCOME_TOTAL, y_axis='y2')] ),

    PlotsGroup(uid='arppu',
               title=u'ARPU & ARPPU (Average Revenue per Active & Paying User)',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.ARPPU, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ARPPU_IN_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ARPU, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.ARPU_IN_MONTH, y_axis='y2')] ),

    PlotsGroup(uid='first-payment',
               title=u'Среднее время до 1-ого платежа (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'дни',
               plots=[Plot(relations.RECORD_TYPE.DAYS_BEFORE_PAYMENT, y_axis='y2')] ),


    PlotsGroup(uid='arpnu',
               title=u'ARPNU (Average Revenue per New User) (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.APRNU_WEEK, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.APRNU_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.APRNU_3_MONTH, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.LTV, y_axis='y2')] ),

    PlotsGroup(uid='revenue',
               title=u'Доход (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.REVENUE, y_axis='y2')] ),

    PlotsGroup(uid='social-group',
               title=u'Распределение доходов по социальным группам (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.INCOME_FROM_FORUM, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_SILENT, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_SINGLES, y_axis='y2')] ),

    PlotsGroup(uid='social-group-percents',
               title=u'% доходов по социальным группам (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'проценты',
               y_value_range=[0, 100],
               y2_value_range=[0, 100],
               plots=[Plot(relations.RECORD_TYPE.INCOME_FROM_FORUM_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_SILENT_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_SINGLES_PERCENTS, y_axis='y2')] ),

    PlotsGroup(uid='goods',
               title=u'Распределение доходов по группам товаров (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_RESET, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_MARKET_COMMISSION, y_axis='y2')] ),

    PlotsGroup(uid='goods-percents',
               title=u'% доходов по группам товаров (за предыдущий месяц)',
               y_label=u'',
               y2_label=u'проценты',
               y_value_range=[0, 100],
               y2_value_range=[0, 100],
               plots=[Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_RESET_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_FROM_GOODS_MARKET_COMMISSION_PERCENTS, y_axis='y2')] ),

    PlotsGroup(uid='income-groups',
               title=u'Численность игроков по размеру трат',
               y_label=u'',
               y2_label=u'количество игроков',
               plots=[Plot(relations.RECORD_TYPE.INCOME_GROUP_0_500, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_500_1000, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_1000_2500, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_2500_10000, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_10000, y_axis='y2')] ),

    PlotsGroup(uid='income-groups-percents',
               title=u'% игроков по размеру трат',
               y_label=u'',
               y2_label=u'проценты',
               y_value_range=[0, 100],
               y2_value_range=[0, 100],
               plots=[Plot(relations.RECORD_TYPE.INCOME_GROUP_0_500_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_500_1000_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_1000_2500_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_2500_10000_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_10000_PERCENTS, y_axis='y2')] ),

    PlotsGroup(uid='income-groups-income',
               title=u'доход по размеру трат',
               y_label=u'',
               y2_label=u'печеньки',
               plots=[Plot(relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME, y_axis='y2')] ),

    PlotsGroup(uid='income-groups-income-percents',
               title=u'% дохода по размеру трат',
               y_label=u'',
               y2_label=u'проценты',
               y_value_range=[0, 100],
               y2_value_range=[0, 100],
               plots=[Plot(relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME_PERCENTS, y_axis='y2'),
                      Plot(relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME_PERCENTS, y_axis='y2')] ),

    ]
