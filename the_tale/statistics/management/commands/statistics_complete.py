# coding: utf-8
import os
from optparse import make_option

from django.core.management.base import BaseCommand

from dext.jinja2 import render
from dext.utils import s11n
from dext.settings import settings

from the_tale.statistics.conf import statistics_settings
from the_tale.statistics.prototypes import RecordPrototype

from the_tale.statistics.metrics import registrations
from the_tale.statistics.metrics import lifetime
from the_tale.statistics.metrics import monetization
from the_tale.statistics.metrics import actual


METRICS = [
        registrations.RegistrationsCompleted,
        registrations.RegistrationsTries,
        registrations.RegistrationsCompletedPercents,
        registrations.AccountsTotal,

        registrations.Referrals,
        registrations.ReferralsTotal,
        registrations.ReferralsPercents,

        actual.Premiums,
        actual.PremiumPercents,
        actual.Active,
        actual.DAU,
        actual.MAU,

        actual.ActiveOlderDay,
        actual.ActiveOlderWeek,
        actual.ActiveOlderMonth,
        actual.ActiveOlder3Month,
        actual.ActiveOlder6Month,
        actual.ActiveOlderYear,

        lifetime.AliveAfterDay,
        lifetime.AliveAfterWeek,
        lifetime.AliveAfterMonth,
        lifetime.AliveAfter3Month,
        lifetime.AliveAfter6Month,
        lifetime.AliveAfterYear,
        lifetime.AliveAfter0,
        lifetime.Lifetime,
        lifetime.LifetimePercent,

        monetization.Payers,
        monetization.Income,
        monetization.ARPPU,
        monetization.ARPU,
        monetization.PU,
        monetization.PUPercents,
        monetization.IncomeTotal,
        monetization.DaysBeforePayment,
        monetization.ARPNUWeek,
        monetization.ARPNUMonth,
        monetization.ARPNU3Month,
        monetization.LTV,

        monetization.Revenue,

        monetization.IncomeFromForum,
        monetization.IncomeFromSilent,
        monetization.IncomeFromGuildMembers,
        monetization.IncomeFromSingles,

        monetization.IncomeFromForumPercents,
        monetization.IncomeFromSilentPercents,
        monetization.IncomeFromGuildMembersPercents,
        monetization.IncomeFromSinglesPercents,

        monetization.IncomeFromGoodsPremium,
        monetization.IncomeFromGoodsEnergy,
        monetization.IncomeFromGoodsChest,
        monetization.IncomeFromGoodsPeferences,
        monetization.IncomeFromGoodsPreferencesReset,
        monetization.IncomeFromGoodsHabits,
        monetization.IncomeFromGoodsAbilities,
        monetization.IncomeFromGoodsClans,

        monetization.IncomeFromGoodsPremiumPercents,
        monetization.IncomeFromGoodsEnergyPercents,
        monetization.IncomeFromGoodsChestPercents,
        monetization.IncomeFromGoodsPeferencesPercents,
        monetization.IncomeFromGoodsPreferencesResetPercents,
        monetization.IncomeFromGoodsHabitsPercents,
        monetization.IncomeFromGoodsAbilitiesPercents,
        monetization.IncomeFromGoodsClansPercents,

        monetization.IncomeGroup0_500,
        monetization.IncomeGroup500_1000,
        monetization.IncomeGroup1000_2500,
        monetization.IncomeGroup2500_10000,
        monetization.IncomeGroup10000,

        monetization.IncomeGroup0_500Percents,
        monetization.IncomeGroup500_1000Percents,
        monetization.IncomeGroup1000_2500Percents,
        monetization.IncomeGroup2500_10000Percents,
        monetization.IncomeGroup10000Percents,

        monetization.IncomeGroupIncome0_500,
        monetization.IncomeGroupIncome500_1000,
        monetization.IncomeGroupIncome1000_2500,
        monetization.IncomeGroupIncome2500_10000,
        monetization.IncomeGroupIncome10000,

        monetization.IncomeGroupIncome0_500Percents,
        monetization.IncomeGroupIncome500_1000Percents,
        monetization.IncomeGroupIncome1000_2500Percents,
        monetization.IncomeGroupIncome2500_10000Percents,
        monetization.IncomeGroupIncome10000Percents
    ]


class Command(BaseCommand):

    help = 'complete statistics'

    option_list = BaseCommand.option_list + ( make_option('-f', '--force-clear',
                                                          action='store_true',
                                                          dest='force-clear',
                                                          help='force clear all metrics'),
                                              make_option('-l', '--log',
                                                          action='store_true',
                                                          dest='verbose',
                                                          help='print log'),
                                              make_option('-r', '--recalculate-last',
                                                          action='store_true',
                                                          dest='recalculate-last',
                                                          help='recalculate last day'),        )

    def handle(self, *args, **options):

        force_clear = options.get('force-clear')
        verbose = options.get('verbose')
        recalculate = options.get('recalculate-last')

        if recalculate:
            for MetricClass in METRICS:
                RecordPrototype._db_filter(date=MetricClass._last_datetime().date(),
                                           type=MetricClass.TYPE).delete()

        for MetricClass in METRICS:
            if force_clear or MetricClass.FULL_CLEAR_RECUIRED:
                if verbose:
                    print 'clear %s' % MetricClass.TYPE
                MetricClass.clear()

        for i, MetricClass in enumerate(METRICS):
            metric = MetricClass()
            if verbose:
                print '[%3d] calculate %s' % (i, metric.TYPE)

            metric.initialize()
            metric.complete_values()


        data_version = int(settings.get(statistics_settings.JS_DATA_FILE_VERSION_KEY, 0))
        data_version += 1
        output_file = statistics_settings.JS_DATA_FILE_LOCATION % data_version

        output_dir_name = os.path.dirname(output_file)
        if not os.path.exists(output_dir_name):
            os.makedirs(output_dir_name, 0755)

        with open(output_file, 'w') as f:
            f.write(render('statistics/js_data.js',
                           {'data': s11n.to_json(RecordPrototype.get_js_data())}).encode('utf-8'))

        settings[statistics_settings.JS_DATA_FILE_VERSION_KEY] = str(data_version)
