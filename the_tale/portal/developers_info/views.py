# coding: utf-8
import itertools
import datetime
import collections

from django.db import models

from dext.views import handler

from common.utils.decorators import staff_required
from common.utils.resources import Resource

from bank.prototypes import AccountPrototype as BankAccountPrototype, InvoicePrototype
from bank.relations import ENTITY_TYPE as BANK_ENTITY_TYPE

from accounts.prototypes import AccountPrototype


class RefererStatistics(collections.namedtuple('RefererStatisticsBase', ('domain', 'count', 'active_accounts', 'premium_accounts', 'active_and_premium', 'premium_currency'))):
    pass

class InvoiceStatistics(collections.namedtuple('InvoiceStatisticsBase', ('operation', 'count', 'premium_currency'))):
    pass


def get_referers_statistics():

    raw_statistics = AccountPrototype.live_query().values('referer_domain').order_by().annotate(models.Count('referer_domain'))

    statistics = []

    for s in raw_statistics:
        domain=s['referer_domain']
        count=s['referer_domain__count']

        query = AccountPrototype.live_query().filter(referer_domain=domain)

        if domain is None:
            count = query.count()

        statistics.append(RefererStatistics(domain=domain,
                                            count=count,
                                            active_accounts=query.filter(active_end_at__gt=datetime.datetime.now()).count(),
                                            premium_accounts=query.filter(premium_end_at__gt=datetime.datetime.now()).count(),
                                            active_and_premium=query.filter(active_end_at__gt=datetime.datetime.now(),
                                                                            premium_end_at__gt=datetime.datetime.now()).count(),
                                            premium_currency=BankAccountPrototype._money_received(from_type=BANK_ENTITY_TYPE.XSOLLA,
                                                                                                  accounts_ids=query.values_list('id', flat=True))))

    statistics = sorted(statistics, key=lambda s: -s.count)

    return statistics

def get_invoice_statistics():

    raw_statistics = InvoicePrototype._model_class.objects.values('operation_uid').order_by().annotate(models.Count('operation_uid'), models.Sum('amount'))

    statistics = []

    for s in raw_statistics:
        statistics.append(InvoiceStatistics(operation=s['operation_uid'],
                                            count=s['operation_uid__count'],
                                            premium_currency=-s['amount__sum']))

    return statistics


class DevelopersInfoResource(Resource):

    @staff_required()
    def initialize(self, *args, **kwargs):
        super(DevelopersInfoResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):

        accounts_total = AccountPrototype._model_class.objects.all().count()
        accounts_bots = AccountPrototype._model_class.objects.filter(is_bot=True).count()
        accounts_registered = AccountPrototype.live_query().count()
        accounts_active = AccountPrototype.live_query().filter(active_end_at__gt=datetime.datetime.now()).count()
        accounts_premium = AccountPrototype.live_query().filter(premium_end_at__gt=datetime.datetime.now()).count()
        accounts_active_and_premium = AccountPrototype.live_query().filter(active_end_at__gt=datetime.datetime.now(),
                                                                           premium_end_at__gt=datetime.datetime.now()).count()

        gold = {}
        gold_total_spent = 0
        gold_total_received = 0
        real_gold_total_spent = 0
        real_gold_total_received = 0

        for record in BANK_ENTITY_TYPE._records:
            spent = -BankAccountPrototype._money_spent(from_type=record)
            received = BankAccountPrototype._money_received(from_type=record)
            gold[record.text] = {'spent': spent, 'received': received}

            gold_total_spent += spent
            gold_total_received += received

            if record.is_real:
                real_gold_total_spent += spent
                real_gold_total_received += received

        gold_in_game = gold_total_received - gold_total_spent
        real_gold_in_game = real_gold_total_received - real_gold_total_spent

        return self.template('developers_info/index.html',
                             {'accounts_total': accounts_total,
                              'accounts_bots': accounts_bots,
                              'accounts_registered': accounts_registered,
                              'accounts_active': accounts_active,
                              'accounts_premium': accounts_premium,
                              'accounts_active_and_premium': accounts_active_and_premium,
                              'gold': gold,
                              'gold_total_spent': gold_total_spent,
                              'gold_total_received': gold_total_received,
                              'gold_in_game': gold_in_game,
                              'real_gold_in_game': real_gold_in_game,
                              'referers_statistics': get_referers_statistics(),
                              'invoice_statistics': get_invoice_statistics(),
                              'invoice_count': InvoicePrototype._model_class.objects.all().count(),
                              'page_type': 'index'})

    @handler('mobs-and-artifacts', method='get')
    def mobs_and_artifacts(self): # pylint: disable=R0914
        from game.mobs.storage import mobs_storage
        from game.artifacts.storage import artifacts_storage
        from game.map.relations import TERRAIN
        from game.logic import DEFAULT_HERO_EQUIPMENT

        mobs_without_loot = []
        mobs_without_artifacts = []
        mobs_without_loot_on_first_level = []
        mobs_without_artifacts_on_first_level = []

        for mob in mobs_storage.get_available_mobs_list(level=999999):
            if not mob.loot:
                mobs_without_loot.append(mob)
            elif not any(loot.level == mob.level for loot in mob.loot):
                mobs_without_loot_on_first_level.append(mob)

            if not mob.artifacts:
                mobs_without_artifacts.append(mob)
            elif not any(artifact.level == mob.level for artifact in mob.artifacts):
                mobs_without_artifacts_on_first_level.append(mob)

        territory_levels_checks = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100]

        mobs_by_territory = { terrain_str:[0]*len(territory_levels_checks) for terrain_str in TERRAIN._ID_TO_STR.values() }

        for mob in mobs_storage.get_available_mobs_list(level=999999):
            for terrain in mob.terrains:
                for i, level in enumerate(territory_levels_checks):
                    if level >= mob.level:
                        mobs_by_territory[TERRAIN._ID_TO_STR[terrain]][i] += 1

        del mobs_by_territory['WATER_SHOAL']
        del mobs_by_territory['WATER_DEEP']

        mobs_by_territory = sorted(mobs_by_territory.items(), key=lambda x: x[1][-1])


        artifacts_without_mobs = []

        for artifact in itertools.chain(artifacts_storage.artifacts, artifacts_storage.loot):
            if artifact.uuid not in DEFAULT_HERO_EQUIPMENT._ALL and artifact.mob is None:
                artifacts_without_mobs.append(artifact)

        return self.template('developers_info/mobs_and_artifacts.html',
                             {'page_type': 'mobs_and_artifacts',
                              'mobs_without_loot': mobs_without_loot,
                              'mobs_without_artifacts': mobs_without_artifacts,
                              'mobs_without_loot_on_first_level': mobs_without_loot_on_first_level,
                              'mobs_without_artifacts_on_first_level': mobs_without_artifacts_on_first_level,
                              'mobs_by_territory': mobs_by_territory,
                              'territory_levels_checks': territory_levels_checks,
                              'artifacts_without_mobs': artifacts_without_mobs})
