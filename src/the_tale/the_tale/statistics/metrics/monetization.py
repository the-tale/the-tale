
import smart_imports

smart_imports.all()


ACCEPTED_INVOICE_FILTER = django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED)


class Payers(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.PAYERS
    PREFETCH_DELTA = datetime.timedelta(days=1)

    def initialize(self):
        super(Payers, self).initialize()
        invoices = list(bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                                    self.db_date_gte('created_at', date=self.free_date - self.PREFETCH_DELTA),
                                                                    sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                    currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('created_at', 'recipient_id'))

        self.invoices = {}

        for invoice_data, recipient_id in invoices:
            created_at = invoice_data.date()

            if created_at not in self.invoices:
                self.invoices[created_at] = set()

            self.invoices[created_at].add(recipient_id)

    def get_value(self, date):
        return len(self.invoices.get(date, frozenset()))


class PayersInMonth(Payers):
    TYPE = relations.RECORD_TYPE.PAYERS_IN_MONTH
    PREFETCH_DELTA = datetime.timedelta(days=30)

    def get_value(self, date):
        return sum(len(self.invoices.get(date - datetime.timedelta(days=i), frozenset())) for i in range(30))


class Income(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.INCOME
    PREFETCH_DELTA = datetime.timedelta(days=1)

    def initialize(self):
        super(Income, self).initialize()
        query = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                            self.db_date_gte('created_at', date=self.free_date - self.PREFETCH_DELTA),
                                                            sender_type=bank_relations.ENTITY_TYPE.XSOLLA, currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('created_at', 'amount')
        invoices = [(created_at.date(), amount) for created_at, amount in query]

        self.invoices_values = {}
        for created_at, amount in invoices:
            self.invoices_values[created_at] = self.invoices_values.get(created_at, 0) + amount

    def get_value(self, date):
        return self.invoices_values.get(date, 0)


class IncomeInMonth(Income):
    TYPE = relations.RECORD_TYPE.INCOME_IN_MONTH
    PREFETCH_DELTA = datetime.timedelta(days=30)

    def get_value(self, date):
        return sum(self.invoices_values.get(date - datetime.timedelta(days=i), 0) for i in range(30))


class IncomeTotal(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.INCOME_TOTAL

    def initialize(self):
        super(IncomeTotal, self).initialize()
        query = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                            self.db_date_gte('created_at'),
                                                            sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                            currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('created_at', 'amount')
        invoices = [(created_at.date(), amount) for created_at, amount in query]

        invoices_values = {}
        for created_at, amount in invoices:
            invoices_values[created_at] = invoices_values.get(created_at, 0) + amount

        income = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                             self.db_date_lt('created_at'),
                                                             sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                             currency=bank_relations.CURRENCY_TYPE.PREMIUM).aggregate(income=django_models.Sum('amount'))['income']
        if income is None:
            income = 0

        self.incomes = {}

        for date in utils_logic.days_range(*self._get_interval()):
            income += invoices_values.get(date, 0)
            self.incomes[date] = income

    def get_value(self, date):
        return self.incomes[date]


class ARPPU(base.BaseFractionCombination):
    TYPE = relations.RECORD_TYPE.ARPPU
    SOURCES = [relations.RECORD_TYPE.INCOME,
               relations.RECORD_TYPE.PAYERS]


class ARPU(base.BaseFractionCombination):
    TYPE = relations.RECORD_TYPE.ARPU
    SOURCES = [relations.RECORD_TYPE.INCOME,
               relations.RECORD_TYPE.DAU]


class ARPPUInMonth(base.BaseFractionCombination):
    TYPE = relations.RECORD_TYPE.ARPPU_IN_MONTH
    SOURCES = [relations.RECORD_TYPE.INCOME_IN_MONTH,
               relations.RECORD_TYPE.PAYERS_IN_MONTH]


class ARPUInMonth(base.BaseFractionCombination):
    TYPE = relations.RECORD_TYPE.ARPU_IN_MONTH
    SOURCES = [relations.RECORD_TYPE.INCOME_IN_MONTH,
               relations.RECORD_TYPE.MAU]


class DaysBeforePayment(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.DAYS_BEFORE_PAYMENT
    FULL_CLEAR_RECUIRED = True
    PERIOD = 30

    def get_value(self, date):
        query = accounts_prototypes.AccountPrototype._db_filter(is_fast=False, is_bot=False)

        # do not use accounts registered before payments turn on
        query = query.filter(self.db_date_interval('created_at', date=date, days=-self.PERIOD),
                             self.db_date_gte('created_at', date=conf.settings.PAYMENTS_START_DATE.date()))
        accounts = dict(query.values_list('id', 'created_at'))

        invoices = list(bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                                    sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                    currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                                    recipient_id__in=list(accounts.keys())).values_list('created_at', 'recipient_id'))

        account_ids = [id_ for created_at, id_ in invoices]

        if not account_ids:
            return 0

        delays = {account_id: min([(created_at - accounts[account_id])
                                   for created_at, id_ in invoices
                                   if id_ == account_id])
                  for account_id in account_ids}

        total_time = functools.reduce(lambda s, v: s + v, list(delays.values()), datetime.timedelta(seconds=0))

        days = float(total_time.total_seconds()) / len(account_ids) / (24 * 60 * 60)

        return days


class ARPNU(base.BaseMetric):
    TYPE = None
    FULL_CLEAR_RECUIRED = True
    DAYS = NotImplemented
    PERIOD = 30

    def get_value(self, date):
        query = accounts_prototypes.AccountPrototype._db_filter(self.db_date_interval('created_at', date=date, days=-self.PERIOD),
                                                                is_fast=False,
                                                                is_bot=False)
        accounts = list(query.values_list('id', 'created_at'))

        if not accounts:
            return 0

        total_income = 0
        for account_id, created_at in accounts:
            income = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                                 self.db_date_interval('created_at', date=created_at, days=self.DAYS),
                                                                 sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                 currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                                 recipient_id=account_id).aggregate(income=django_models.Sum('amount'))['income']
            if income is not None:
                total_income += income

        return float(total_income) / len(accounts)

    def _get_interval(self):
        return (self.free_date, (datetime.datetime.now() - datetime.timedelta(days=self.DAYS)).date())


class ARPNUWeek(ARPNU):
    TYPE = relations.RECORD_TYPE.APRNU_WEEK
    DAYS = 7


class ARPNUMonth(ARPNU):
    TYPE = relations.RECORD_TYPE.APRNU_MONTH
    DAYS = 30


class ARPNU3Month(ARPNU):
    TYPE = relations.RECORD_TYPE.APRNU_3_MONTH
    DAYS = 90


class LTV(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.LTV
    FULL_CLEAR_RECUIRED = True
    PERIOD = 7

    def get_value(self, date):
        query = accounts_prototypes.AccountPrototype._db_filter(self.db_date_interval('created_at', date=date, days=-self.PERIOD),
                                                                is_fast=False,
                                                                is_bot=False)
        accounts_ids = list(query.values_list('id', flat=True))

        if not accounts_ids:
            return 0

        total_income = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                                   sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                   currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                                   recipient_id__in=accounts_ids).aggregate(income=django_models.Sum('amount'))['income']

        if total_income is None:
            return 0

        return float(total_income) / len(accounts_ids)


class IncomeFromGroupsBase(base.BaseMetric):
    TYPE = None
    PERIOD = 30

    @classmethod
    def filter_recipients(cls, ids):
        raise NotImplementedError

    def get_value(self, date):
        invoices = list(bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                                    self.db_date_interval('created_at', date=date, days=-self.PERIOD),
                                                                    sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                    currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id', 'amount'))

        if not invoices:
            return 0

        recipients = set(self.filter_recipients(next(zip(*invoices))))

        return sum([amount for recipient_id, amount in invoices if recipient_id in recipients], 0)


class IncomeFromForum(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_FORUM

    @classmethod
    def filter_recipients(cls, ids):
        return set(forum_models.Post.objects.filter(author__in=ids).values_list('author_id', flat=True))


class IncomeFromSilent(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_SILENT

    @classmethod
    def filter_recipients(cls, ids):
        return set(ids) - set(forum_models.Post.objects.filter(author__in=ids).values_list('author_id', flat=True))


class IncomeFromGuildMembers(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS

    @classmethod
    def filter_recipients(cls, ids):
        return set(accounts_prototypes.AccountPrototype._db_filter(membership__account__in=ids).values_list('id', flat=True))


class IncomeFromSingles(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_SINGLES

    @classmethod
    def filter_recipients(cls, ids):
        return set(accounts_prototypes.AccountPrototype._db_exclude(membership__account__in=ids).values_list('id', flat=True))


class IncomeFromGoodsBase(base.BaseMetric):
    TYPE = None
    GROUP_PREFIX = NotImplemented
    PERIOD = 30

    def selector(self):
        return django_models.Q(operation_uid__contains=self.GROUP_PREFIX)

    def get_value(self, date):
        income = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                             self.selector(),
                                                             self.db_date_interval('created_at', date=date, days=-self.PERIOD),
                                                             sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                             currency=bank_relations.CURRENCY_TYPE.PREMIUM).aggregate(income=django_models.Sum('amount'))['income']

        if income is None:
            return 0

        return -income


class IncomeFromGoodsPremium(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.PREMIUM.uid_prefix


class IncomeFromGoodsEnergy(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.ENERGY.uid_prefix


class IncomeFromGoodsChest(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.CHEST.uid_prefix


class IncomeFromGoodsPeferences(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.PREFERENCES.uid_prefix


class IncomeFromGoodsPreferencesReset(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_RESET
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.PREFERENCES_RESET.uid_prefix


class IncomeFromGoodsHabits(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.HABITS.uid_prefix


class IncomeFromGoodsAbilities(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.ABILITIES.uid_prefix


class IncomeFromGoodsClans(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS
    GROUP_PREFIX = '<%s' % shop_relations.GOODS_GROUP.CLANS.uid_prefix


class IncomeFromGoodsMarketCommission(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_MARKET_COMMISSION
    GROUP_PREFIX = shop_conf.settings.MARKET_COMMISSION_OPERATION_UID


class IncomeFromTransferMoneyCommission(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_TRANSFER_MONEY_COMMISSION
    GROUP_PREFIX = accounts_conf.settings.COMMISION_TRANSACTION_UID


class IncomeFromGoodsOther(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_OTHER
    GROUP = None

    def selector(self):
        return ~(django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsPremium.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsEnergy.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsChest.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsPeferences.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsPreferencesReset.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsHabits.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsAbilities.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsClans.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromGoodsMarketCommission.GROUP_PREFIX) |
                 django_models.Q(operation_uid__contains='<%s' % IncomeFromTransferMoneyCommission.GROUP_PREFIX))


class PU(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.PU

    def get_value(self, date):
        return bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                           self.db_date_lte('created_at', date=date),
                                                           sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                           currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id').order_by('recipient_id').distinct().count()


class PUPercents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.PU_PERCENTS
    SOURCES = [relations.RECORD_TYPE.PU,
               relations.RECORD_TYPE.REGISTRATIONS_TOTAL]


class IncomeGroupBase(base.BaseMetric):
    TYPE = None
    BORDERS = NotImplemented

    def get_value(self, date):
        incomes = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                              self.db_date_lte('created_at', date=date),
                                                              sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                              currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id', 'amount')

        accounts_incomes = {}
        for recipient_id, amount in incomes:
            accounts_incomes[recipient_id] = accounts_incomes.get(recipient_id, 0) + amount

        return len([True
                    for amount in accounts_incomes.values()
                    if self.BORDERS[0] < amount <= self.BORDERS[1]])


class IncomeGroup0_500(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500
    BORDERS = (0, 500)


class IncomeGroup500_1000(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000
    BORDERS = (500, 1000)


class IncomeGroup1000_2500(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500
    BORDERS = (1000, 2500)


class IncomeGroup2500_10000(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000
    BORDERS = (2500, 10000)


class IncomeGroup10000(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000
    BORDERS = (10000, 9999999999999)


class IncomeGroup0_500Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_0_500,
               relations.RECORD_TYPE.PU]


class IncomeGroup500_1000Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_500_1000,
               relations.RECORD_TYPE.PU]


class IncomeGroup1000_2500Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_1000_2500,
               relations.RECORD_TYPE.PU]


class IncomeGroup2500_10000Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_2500_10000,
               relations.RECORD_TYPE.PU]


class IncomeGroup10000Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_10000,
               relations.RECORD_TYPE.PU]


class IncomeGroupIncomeBase(base.BaseMetric):
    TYPE = None
    BORDERS = NotImplemented

    def get_value(self, date):
        incomes = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                              self.db_date_lte('created_at', date=date),
                                                              sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                              currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id', 'amount')

        accounts_incomes = {}
        for recipient_id, amount in incomes:
            accounts_incomes[recipient_id] = accounts_incomes.get(recipient_id, 0) + amount

        return sum([amount
                    for amount in accounts_incomes.values()
                    if self.BORDERS[0] < amount <= self.BORDERS[1]], 0)


class IncomeGroupIncome0_500(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME
    BORDERS = (0, 500)


class IncomeGroupIncome500_1000(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME
    BORDERS = (500, 1000)


class IncomeGroupIncome1000_2500(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME
    BORDERS = (1000, 2500)


class IncomeGroupIncome2500_10000(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME
    BORDERS = (2500, 10000)


class IncomeGroupIncome10000(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME
    BORDERS = (10000, 9999999999999)


class IncomeGroupIncome0_500Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME,
               relations.RECORD_TYPE.INCOME_TOTAL]


class IncomeGroupIncome500_1000Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME,
               relations.RECORD_TYPE.INCOME_TOTAL]


class IncomeGroupIncome1000_2500Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME,
               relations.RECORD_TYPE.INCOME_TOTAL]


class IncomeGroupIncome2500_10000Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME,
               relations.RECORD_TYPE.INCOME_TOTAL]


class IncomeGroupIncome10000Percents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME,
               relations.RECORD_TYPE.INCOME_TOTAL]


class Revenue(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.REVENUE
    FULL_CLEAR_RECUIRED = True  # change to False after v0.3.18
    DAYS = None
    PERIOD = 30

    def get_value(self, date):
        income = bank_prototypes.InvoicePrototype._db_filter(ACCEPTED_INVOICE_FILTER,
                                                             self.db_date_interval('created_at', date=date, days=-self.PERIOD),
                                                             sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                             currency=bank_relations.CURRENCY_TYPE.PREMIUM).aggregate(income=django_models.Sum('amount'))['income']
        if income is None:
            return 0

        return income


_FORUM_GROUPS = [relations.RECORD_TYPE.INCOME_FROM_FORUM,
                 relations.RECORD_TYPE.INCOME_FROM_SILENT]

_GUILDS_GROUPS = [relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS,
                  relations.RECORD_TYPE.INCOME_FROM_SINGLES]


class IncomeFromForumPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_FORUM_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_FORUM] + _FORUM_GROUPS


class IncomeFromSilentPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_SILENT_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_SILENT] + _FORUM_GROUPS


class IncomeFromGuildMembersPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS] + _GUILDS_GROUPS


class IncomeFromSinglesPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_SINGLES_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_SINGLES] + _GUILDS_GROUPS


_GOODS_GROUPS = [relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_RESET,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS,
                 relations.RECORD_TYPE.INCOME_FROM_GOODS_MARKET_COMMISSION,
                 relations.RECORD_TYPE.INCOME_FROM_TRANSFER_MONEY_COMMISSION]


class IncomeFromGoodsPremiumPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM] + _GOODS_GROUPS


class IncomeFromGoodsEnergyPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY] + _GOODS_GROUPS


class IncomeFromGoodsChestPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST] + _GOODS_GROUPS


class IncomeFromGoodsPeferencesPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES] + _GOODS_GROUPS


class IncomeFromGoodsPreferencesResetPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_RESET_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES_RESET] + _GOODS_GROUPS


class IncomeFromGoodsHabitsPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS] + _GOODS_GROUPS


class IncomeFromGoodsAbilitiesPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES] + _GOODS_GROUPS


class IncomeFromGoodsClansPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS] + _GOODS_GROUPS


class IncomeFromGoodsMarketCommissionPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_MARKET_COMMISSION_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_GOODS_MARKET_COMMISSION] + _GOODS_GROUPS


class IncomeFromTransferMoneyCommissionPercents(base.BasePercentsFromSumCombination):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_TRANSFER_MONEY_COMMISSION_PERCENTS
    SOURCES = [relations.RECORD_TYPE.INCOME_FROM_TRANSFER_MONEY_COMMISSION] + _GOODS_GROUPS
