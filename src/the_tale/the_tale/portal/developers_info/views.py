
import smart_imports

smart_imports.all()


InvoiceQuery = bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED))


class RefererStatistics(collections.namedtuple('RefererStatisticsBase', ('domain', 'count', 'active_accounts', 'premium_accounts', 'active_and_premium', 'premium_currency'))):

    def __add__(self, s):
        return RefererStatistics(domain=self.domain,
                                 count=self.count + s.count,
                                 active_accounts=self.active_accounts + s.active_accounts,
                                 premium_accounts=self.premium_accounts + s.premium_accounts,
                                 active_and_premium=self.active_and_premium + s.active_and_premium,
                                 premium_currency=self.premium_currency + s.premium_currency)


class InvoiceStatistics(collections.namedtuple('InvoiceStatisticsBase', ('operation', 'count', 'premium_currency'))):
    pass


def get_referers_statistics():

    raw_statistics = accounts_prototypes.AccountPrototype.live_query().values('referer_domain').order_by().annotate(django_models.Count('referer_domain'))

    statistics = {}

    for s in raw_statistics:
        domain = s['referer_domain']

        count = s['referer_domain__count']

        query = accounts_prototypes.AccountPrototype.live_query().filter(referer_domain=domain)

        if domain is None:
            count = query.count()

        target_domain = domain

        if target_domain and target_domain.endswith('livejournal.com'):  # hide all domains username.livejournal.com (to hide there payment info)
            target_domain = 'livejournal.com'

        st = RefererStatistics(domain=target_domain,
                               count=count,
                               active_accounts=query.filter(active_end_at__gt=datetime.datetime.now()).count(),
                               premium_accounts=query.filter(premium_end_at__gt=datetime.datetime.now()).count(),
                               active_and_premium=query.filter(active_end_at__gt=datetime.datetime.now(),
                                                               premium_end_at__gt=datetime.datetime.now()).count(),
                               premium_currency=bank_prototypes.AccountPrototype._money_received(from_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                                                 accounts_ids=query.values_list('id', flat=True)))

        if st.domain in statistics:
            statistics[st.domain] = statistics[st.domain] + st
        else:
            statistics[st.domain] = st

    statistics = sorted(list(statistics.values()), key=lambda s: -s.count)

    return statistics


def get_invoice_statistics():

    raw_statistics = InvoiceQuery.values('operation_uid').order_by().annotate(django_models.Count('operation_uid'), django_models.Sum('amount'))

    statistics = []

    for s in raw_statistics:
        statistics.append(InvoiceStatistics(operation=s['operation_uid'],
                                            count=s['operation_uid__count'],
                                            premium_currency=-s['amount__sum']))

    return statistics


def get_repeatable_payments_statistics():
    # группы по количеству оплат
    payments_count = collections.Counter(InvoiceQuery.filter(sender_type=bank_relations.ENTITY_TYPE.XSOLLA).values_list('recipient_id', flat=True))
    payments_count_groups = collections.Counter(list(payments_count.values()))

    # группы по заплаченным деньгам
    gold_count = InvoiceQuery.filter(sender_type=bank_relations.ENTITY_TYPE.XSOLLA).values_list('recipient_id', 'amount')
    accounts_spend = {}
    for account_id, amount in gold_count:
        accounts_spend[account_id] = accounts_spend.get(account_id, 0) + amount

    payment_sum_groups = {}

    for amount in list(accounts_spend.values()):
        for group in relations.PAYMENT_GROUPS.records:
            if amount < group.top_border:
                payment_sum_groups[group.value] = payment_sum_groups.get(group.value, 0) + 1
                break

    # группы по повторным подпискам
    subscriptions_count = collections.Counter(InvoiceQuery.filter(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                  operation_uid__startswith='ingame-purchase-<subscription').values_list('recipient_id', flat=True))
    subscriptions_count_groups = collections.Counter(list(subscriptions_count.values()))

    # группы по повторным покупкам энергии
    energy_count = collections.Counter(InvoiceQuery.filter(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                           operation_uid__startswith='ingame-purchase-<energy-').values_list('recipient_id', flat=True))
    energy_count_groups = collections.Counter(list(energy_count.values()))

    return {'payments_count_groups': sorted(payments_count_groups.items()),
            'payment_sum_groups': [(relations.PAYMENT_GROUPS(group_id).text, count) for group_id, count in sorted(payment_sum_groups.items())],
            'subscriptions_count_groups': sorted(subscriptions_count_groups.items()),
            'energy_count_groups': sorted(energy_count_groups.items())}


class DevelopersInfoResource(utils_resources.Resource):

    @utils_decorators.staff_required()
    def initialize(self, *args, **kwargs):
        super(DevelopersInfoResource, self).initialize(*args, **kwargs)

    @dext_old_views.handler('', method='get')
    def index(self):

        registration_attemps_number = accounts_prototypes.AccountPrototype._model_class.objects.all().aggregate(django_models.Max('id'))['id__max']
        accounts_total = accounts_prototypes.AccountPrototype._model_class.objects.all().count()
        accounts_bots = accounts_prototypes.AccountPrototype._model_class.objects.filter(is_bot=True).count()
        accounts_registered = accounts_prototypes.AccountPrototype.live_query().count()
        accounts_active = accounts_prototypes.AccountPrototype.live_query().filter(active_end_at__gt=datetime.datetime.now()).count()
        accounts_premium = accounts_prototypes.AccountPrototype.live_query().filter(premium_end_at__gt=datetime.datetime.now()).count()
        accounts_active_and_premium = accounts_prototypes.AccountPrototype.live_query().filter(active_end_at__gt=datetime.datetime.now(),
                                                                                               premium_end_at__gt=datetime.datetime.now()).count()

        accounts_referrals = accounts_prototypes.AccountPrototype.live_query().exclude(referral_of=None).count()
        accounts_referrals_and_premium = accounts_prototypes.AccountPrototype.live_query().exclude(referral_of=None).filter(premium_end_at__gt=datetime.datetime.now()).count()
        accounts_referrals_and_active = accounts_prototypes.AccountPrototype.live_query().exclude(referral_of=None).filter(active_end_at__gt=datetime.datetime.now(),
                                                                                                                           premium_end_at__gt=datetime.datetime.now()).count()

        gold = {}
        gold_total_spent = 0
        gold_total_received = 0
        real_gold_total_spent = 0
        real_gold_total_received = 0

        for record in bank_relations.ENTITY_TYPE.records:
            spent = -bank_prototypes.AccountPrototype._money_spent(from_type=record)
            received = bank_prototypes.AccountPrototype._money_received(from_type=record)
            gold[record.text] = {'spent': spent, 'received': received}

            gold_total_spent += spent
            gold_total_received += received

            if record.is_real:
                real_gold_total_spent += spent
                real_gold_total_received += received

        gold_in_game = gold_total_received - gold_total_spent
        real_gold_in_game = real_gold_total_received - real_gold_total_spent

        return self.template('developers_info/index.html',
                             {'registration_attemps_number': registration_attemps_number,
                              'accounts_total': accounts_total,
                              'accounts_bots': accounts_bots,
                              'accounts_registered': accounts_registered,
                              'accounts_active': accounts_active,
                              'accounts_premium': accounts_premium,
                              'accounts_active_and_premium': accounts_active_and_premium,
                              'accounts_referrals': accounts_referrals,
                              'accounts_referrals_and_premium': accounts_referrals_and_premium,
                              'accounts_referrals_and_active': accounts_referrals_and_active,
                              'gold': gold,
                              'gold_total_spent': gold_total_spent,
                              'gold_total_received': gold_total_received,
                              'gold_in_game': gold_in_game,
                              'real_gold_in_game': real_gold_in_game,
                              'referers_statistics': get_referers_statistics(),
                              'invoice_statistics': get_invoice_statistics(),
                              'invoice_count': InvoiceQuery.count(),
                              'repeatable_payments_statistics': get_repeatable_payments_statistics(),
                              'PAYMENT_GROUPS': relations.PAYMENT_GROUPS,
                              'PREMIUM_DAYS_FOR_HERO_OF_THE_DAY': portal_conf.settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY,
                              'page_type': 'index'})

    @dext_old_views.handler('mobs-and-artifacts', method='get')
    def mobs_and_artifacts(self):  # pylint: disable=R0914
        mobs_without_loot = []
        mobs_without_artifacts = []
        mobs_without_loot_on_first_level = []
        mobs_without_artifacts_on_first_level = []

        for mob in mobs_storage.mobs.get_all_mobs_for_level(level=999999):
            if not mob.loot:
                mobs_without_loot.append(mob)
            elif not any(loot.level == mob.level for loot in mob.loot):
                mobs_without_loot_on_first_level.append(mob)

            if not mob.artifacts:
                mobs_without_artifacts.append(mob)
            elif not any(artifact.level == mob.level for artifact in mob.artifacts):
                mobs_without_artifacts_on_first_level.append(mob)

        territory_levels_checks = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100]

        mobs_by_territory = {terrain.name: [0] * len(territory_levels_checks) for terrain in map_relations.TERRAIN.records}

        for mob in mobs_storage.mobs.get_all_mobs_for_level(level=999999):
            for terrain in mob.terrains:
                for i, level in enumerate(territory_levels_checks):
                    if level >= mob.level:
                        mobs_by_territory[terrain.name][i] += 1

        del mobs_by_territory['WATER_SHOAL']
        del mobs_by_territory['WATER_DEEP']

        mobs_by_territory = sorted(list(mobs_by_territory.items()), key=lambda x: x[1][-1])

        artifacts_without_mobs = []

        for artifact in itertools.chain(artifacts_storage.artifacts.artifacts, artifacts_storage.artifacts.loot):
            if artifact.uuid not in heroes_relations.EQUIPMENT_SLOT.index_default and artifact.mob is None:
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
