
import smart_imports

smart_imports.all()

from the_tale.statistics.metrics import registrations
from the_tale.statistics.metrics import lifetime
from the_tale.statistics.metrics import monetization
from the_tale.statistics.metrics import actual
from the_tale.statistics.metrics import forum
from the_tale.statistics.metrics import bills
from the_tale.statistics.metrics import folclor


METRICS = [
    statistics_metrics_registrations.RegistrationsCompleted,
    statistics_metrics_registrations.RegistrationsTries,
    statistics_metrics_registrations.RegistrationsCompletedPercents,

    statistics_metrics_registrations.RegistrationsCompletedInMonth,
    statistics_metrics_registrations.RegistrationsTriesInMonth,
    statistics_metrics_registrations.RegistrationsCompletedPercentsInMonth,

    statistics_metrics_registrations.AccountsTotal,

    statistics_metrics_registrations.Referrals,
    statistics_metrics_registrations.ReferralsTotal,
    statistics_metrics_registrations.ReferralsPercents,

    statistics_metrics_registrations.ReferralsInMonth,

    statistics_metrics_actual.Premiums,
    statistics_metrics_actual.InfinitPremiums,
    statistics_metrics_actual.PremiumPercents,
    statistics_metrics_actual.Active,
    statistics_metrics_actual.DAU,
    statistics_metrics_actual.MAU,

    statistics_metrics_actual.ActiveOlderDay,
    statistics_metrics_actual.ActiveOlderWeek,
    statistics_metrics_actual.ActiveOlderMonth,
    statistics_metrics_actual.ActiveOlder3Month,
    statistics_metrics_actual.ActiveOlder6Month,
    statistics_metrics_actual.ActiveOlderYear,

    statistics_metrics_lifetime.AliveAfterDay,
    statistics_metrics_lifetime.AliveAfterWeek,
    statistics_metrics_lifetime.AliveAfterMonth,
    statistics_metrics_lifetime.AliveAfter3Month,
    statistics_metrics_lifetime.AliveAfter6Month,
    statistics_metrics_lifetime.AliveAfterYear,
    statistics_metrics_lifetime.AliveAfter0,
    statistics_metrics_lifetime.Lifetime,
    statistics_metrics_lifetime.LifetimePercent,

    statistics_metrics_monetization.Payers,
    statistics_metrics_monetization.Income,
    statistics_metrics_monetization.PayersInMonth,
    statistics_metrics_monetization.IncomeInMonth,
    statistics_metrics_monetization.ARPPU,
    statistics_metrics_monetization.ARPU,
    statistics_metrics_monetization.ARPPUInMonth,
    statistics_metrics_monetization.ARPUInMonth,
    statistics_metrics_monetization.PU,
    statistics_metrics_monetization.PUPercents,
    statistics_metrics_monetization.IncomeTotal,
    statistics_metrics_monetization.DaysBeforePayment,
    statistics_metrics_monetization.ARPNUWeek,
    statistics_metrics_monetization.ARPNUMonth,
    statistics_metrics_monetization.ARPNU3Month,
    statistics_metrics_monetization.LTV,

    statistics_metrics_monetization.Revenue,

    statistics_metrics_monetization.IncomeFromForum,
    statistics_metrics_monetization.IncomeFromSilent,
    statistics_metrics_monetization.IncomeFromGuildMembers,
    statistics_metrics_monetization.IncomeFromSingles,

    statistics_metrics_monetization.IncomeFromForumPercents,
    statistics_metrics_monetization.IncomeFromSilentPercents,
    statistics_metrics_monetization.IncomeFromGuildMembersPercents,
    statistics_metrics_monetization.IncomeFromSinglesPercents,

    statistics_metrics_monetization.IncomeFromGoodsPremium,
    statistics_metrics_monetization.IncomeFromGoodsEnergy,
    statistics_metrics_monetization.IncomeFromGoodsChest,
    statistics_metrics_monetization.IncomeFromGoodsPeferences,
    statistics_metrics_monetization.IncomeFromGoodsPreferencesReset,
    statistics_metrics_monetization.IncomeFromGoodsHabits,
    statistics_metrics_monetization.IncomeFromGoodsAbilities,
    statistics_metrics_monetization.IncomeFromGoodsClans,
    statistics_metrics_monetization.IncomeFromGoodsMarketCommission,
    statistics_metrics_monetization.IncomeFromTransferMoneyCommission,

    statistics_metrics_monetization.IncomeFromGoodsPremiumPercents,
    statistics_metrics_monetization.IncomeFromGoodsEnergyPercents,
    statistics_metrics_monetization.IncomeFromGoodsChestPercents,
    statistics_metrics_monetization.IncomeFromGoodsPeferencesPercents,
    statistics_metrics_monetization.IncomeFromGoodsPreferencesResetPercents,
    statistics_metrics_monetization.IncomeFromGoodsHabitsPercents,
    statistics_metrics_monetization.IncomeFromGoodsAbilitiesPercents,
    statistics_metrics_monetization.IncomeFromGoodsClansPercents,
    statistics_metrics_monetization.IncomeFromGoodsMarketCommissionPercents,
    statistics_metrics_monetization.IncomeFromTransferMoneyCommissionPercents,

    statistics_metrics_monetization.IncomeGroup0_500,
    statistics_metrics_monetization.IncomeGroup500_1000,
    statistics_metrics_monetization.IncomeGroup1000_2500,
    statistics_metrics_monetization.IncomeGroup2500_10000,
    statistics_metrics_monetization.IncomeGroup10000,

    statistics_metrics_monetization.IncomeGroup0_500Percents,
    statistics_metrics_monetization.IncomeGroup500_1000Percents,
    statistics_metrics_monetization.IncomeGroup1000_2500Percents,
    statistics_metrics_monetization.IncomeGroup2500_10000Percents,
    statistics_metrics_monetization.IncomeGroup10000Percents,

    statistics_metrics_monetization.IncomeGroupIncome0_500,
    statistics_metrics_monetization.IncomeGroupIncome500_1000,
    statistics_metrics_monetization.IncomeGroupIncome1000_2500,
    statistics_metrics_monetization.IncomeGroupIncome2500_10000,
    statistics_metrics_monetization.IncomeGroupIncome10000,

    statistics_metrics_monetization.IncomeGroupIncome0_500Percents,
    statistics_metrics_monetization.IncomeGroupIncome500_1000Percents,
    statistics_metrics_monetization.IncomeGroupIncome1000_2500Percents,
    statistics_metrics_monetization.IncomeGroupIncome2500_10000Percents,
    statistics_metrics_monetization.IncomeGroupIncome10000Percents,

    statistics_metrics_forum.Posts,
    statistics_metrics_forum.PostsInMonth,
    statistics_metrics_forum.PostsTotal,
    statistics_metrics_forum.Threads,
    statistics_metrics_forum.ThreadsInMonth,
    statistics_metrics_forum.ThreadsTotal,
    statistics_metrics_forum.PostsPerThreadInMonth,

    statistics_metrics_bills.Bills,
    statistics_metrics_bills.BillsInMonth,
    statistics_metrics_bills.BillsTotal,
    statistics_metrics_bills.Votes,
    statistics_metrics_bills.VotesInMonth,
    statistics_metrics_bills.VotesTotal,
    statistics_metrics_bills.VotesPerBillInMonth,

    statistics_metrics_folclor.Posts,
    statistics_metrics_folclor.PostsInMonth,
    statistics_metrics_folclor.PostsTotal,
    statistics_metrics_folclor.Votes,
    statistics_metrics_folclor.VotesInMonth,
    statistics_metrics_folclor.VotesTotal,
    statistics_metrics_folclor.VotesPerPostInMonth
]


class Command(django_management.BaseCommand):

    help = 'complete statistics'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-f', '--force-clear', action='store_true', dest='force-clear', help='force clear all metrics')
        parser.add_argument('-l', '--log', action='store_true', dest='verbose', help='print log')
        parser.add_argument('-r', '--recalculate-last', action='store_true', dest='recalculate-last', help='recalculate last day')

    def handle(self, *args, **options):

        force_clear = options.get('force-clear')
        verbose = options.get('verbose')
        recalculate = options.get('recalculate-last')

        if recalculate:
            for MetricClass in METRICS:
                prototypes.RecordPrototype._db_filter(date=MetricClass._last_datetime().date(),
                                                      type=MetricClass.TYPE).delete()

        for MetricClass in METRICS:
            if force_clear or MetricClass.FULL_CLEAR_RECUIRED:
                if verbose:
                    print('clear %s' % MetricClass.TYPE)
                MetricClass.clear()

        for i, MetricClass in enumerate(METRICS):
            metric = MetricClass()
            if verbose:
                print('[%3d] calculate %s' % (i, metric.TYPE))

            metric.initialize()
            metric.complete_values()

        models.FullStatistics.objects.all().delete()
        models.FullStatistics.objects.create(data=prototypes.RecordPrototype.get_js_data())
