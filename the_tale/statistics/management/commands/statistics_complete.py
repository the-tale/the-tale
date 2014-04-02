# coding: utf-8

from django.core.management.base import BaseCommand

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

        monetization.IncomeFromForum,
        monetization.IncomeFromSilent,
        monetization.IncomeFromGuildMembers,
        monetization.IncomeFromSingles,

        monetization.IncomeFromGoodsPremium,
        monetization.IncomeFromGoodsEnergy,
        monetization.IncomeFromGoodsChest,
        monetization.IncomeFromGoodsOther,
        monetization.IncomeFromGoodsPeferences,
        monetization.IncomeFromGoodsPreferencesReset,
        monetization.IncomeFromGoodsHabits,
        monetization.IncomeFromGoodsAbilities,
        monetization.IncomeFromGoodsClans,

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
        monetization.IncomeGroupIncome10000Percents,
    ]


class Command(BaseCommand):

    help = 'complete statistics'

    def handle(self, *args, **options):

        for metric in METRICS:
            print 'calculate %s' % metric.TYPE
            metric.clear()
            metric.complete_values()
