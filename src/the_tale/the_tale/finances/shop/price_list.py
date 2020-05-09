
import smart_imports

smart_imports.all()

SUBSCRIPTION_INFINIT_UID = 'subscription-infinit'


PREMIUM_DAYS_DESCRIPTION = '''
<p>
Подписка даёт следующие преимущества:
</p>

<ul>
  <li>герой оказывает влияние на мир;</li>
  <li>можно голосовать;</li>
  <li>получаемые карты судьбы можно продавать на рынке;</li>
  <li>на 50% увеличивается получаемый героем опыт;</li>
  <li>на 50% увеличивается скорость изменения черт;</li>
  <li>на 200% увеличивается максимум энергии (до 72 единиц);</li>
  <li>размер дневника героя увеличен до {DIARY_LOG_LENGTH_PREMIUM} сообщений;</li>
  <li>жизнь героя не замедляется при длительном отсутствии игрока в игре;</li>
  <li>спутник героя не покидает его, когда здоровье спутника опускается до нуля;</li>
  <li>игрок может одновременно создать до {PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS} записей в Книге Судеб.</li>
</ul>
'''.format(DIARY_LOG_LENGTH_PREMIUM=heroes_conf.settings.DIARY_LOG_LENGTH_PREMIUM,
           PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS=c.PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS)


def permanent_purchase(uid, purchase_type, cost, transaction_description):
    return goods.PermanentPurchase(uid=uid,
                                   name=purchase_type.text,
                                   full_name=purchase_type.full_name,
                                   description=purchase_type.description,
                                   cost=cost,
                                   purchase_type=purchase_type,
                                   transaction_description=transaction_description)


SUBSCRIPTIONS = [goods.PremiumDays(uid='subscription-15',
                                   name='15 дней',
                                   full_name='15 дней подписки',
                                   description=PREMIUM_DAYS_DESCRIPTION,
                                   cost=180,
                                   days=15,
                                   transaction_description='Продление подписки на 15 дней.'),

                 goods.PremiumDays(uid='subscription-30',
                                   name='30 дней',
                                   full_name='30 дней подписки',
                                   description=PREMIUM_DAYS_DESCRIPTION,
                                   cost=300,
                                   days=30,
                                   transaction_description='Продление подписки на 30 дней.'),

                 goods.PremiumDays(uid='subscription-90',
                                   name='90 дней',
                                   full_name='90 дней подписки',
                                   description=PREMIUM_DAYS_DESCRIPTION,
                                   cost=750,
                                   days=90,
                                   transaction_description='Продление подписки на 90 дней.'),

                 permanent_purchase(uid=SUBSCRIPTION_INFINIT_UID,
                                    purchase_type=relations.PERMANENT_PURCHASE_TYPE.INFINIT_SUBSCRIPTION,
                                    cost=6000,
                                    transaction_description='Приобретение вечной подписки.')]


PURCHASES_BY_UID = {}

for purchase in SUBSCRIPTIONS:
    if purchase.uid in PURCHASES_BY_UID:
        raise exceptions.DuplicateUIDsInPriceListError()
    PURCHASES_BY_UID[purchase.uid] = purchase
