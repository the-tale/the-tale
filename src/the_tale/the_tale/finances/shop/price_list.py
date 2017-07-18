# coding: utf-8

from the_tale.finances.shop import goods
from the_tale.finances.shop import exceptions
from the_tale.finances.shop import relations
from the_tale.finances.shop.conf import payments_settings

from the_tale.game.heroes import conf as heroes_conf

from the_tale.game.balance import constants as c


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
  <li>игрок может одноврменно создать до {PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS} записей в Книге Судеб.</li>
</ul>
'''.format(DIARY_LOG_LENGTH_PREMIUM=heroes_conf.heroes_settings.DIARY_LOG_LENGTH_PREMIUM,
           PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS=c.PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS)


RANDOM_PREMIUM_CHEST_DESCRIPTION = '''
<p>
Подарите подписку на %(days)s дней случайному активному игроку (не подписчику) и получите один из подарков:
</p>
<ul>
%(gifts)s
</ul>
<p>
Подарки указаны от самого вероятного к самому редкому.
</p>

<p>
Чем больше подписчиков, тем увлекательнее жизнь Пандоры!
</p>
''' % {'gifts': '\n'.join('<li>%s</li>' % reward.description
                          for reward in sorted(relations.RANDOM_PREMIUM_CHEST_REWARD.records, key=lambda r: -r.priority)),
       'days': payments_settings.RANDOM_PREMIUM_DAYS }

def permanent_purchase(uid, purchase_type, cost, transaction_description):
    return goods.PermanentPurchase(uid=uid,
                                   name=purchase_type.text,
                                   full_name=purchase_type.full_name,
                                   description=purchase_type.description,
                                   cost=cost,
                                   purchase_type=purchase_type,
                                   transaction_description=transaction_description)


RANDOM_PREMIUM_CHEST = goods.PurchaseGroup(type=relations.GOODS_GROUP.CHEST,
                                           name='Делай добро и дари подписку!',
                                           short_name='Сделать добро',
                                           description=RANDOM_PREMIUM_CHEST_DESCRIPTION,
                                           items=[ goods.RandomPremiumChest(uid='random-premium-chest',
                                                                            cost=200,
                                                                            description=RANDOM_PREMIUM_CHEST_DESCRIPTION,
                                                                            name='Сделать добро',
                                                                            full_name='Делай добро и дари подписку!',
                                                                            transaction_description='Подписка в подарок случайному игроку') ])


PRICE_GROUPS = [RANDOM_PREMIUM_CHEST,

                goods.PurchaseGroup(type=relations.GOODS_GROUP.PREMIUM,
                                    name='Подписка',
                                    description=PREMIUM_DAYS_DESCRIPTION,
                                    items=[ goods.PremiumDays(uid='subscription-15',
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

                                            permanent_purchase(uid='subscription-infinit',
                                                               purchase_type=relations.PERMANENT_PURCHASE_TYPE.INFINIT_SUBSCRIPTION,
                                                               cost=6000,
                                                               transaction_description='Приобретение вечной подписки.')  ]),
                ]



PURCHASES_BY_UID = {}

for group in PRICE_GROUPS:
    for purchase in group.items:
        if purchase.uid in PURCHASES_BY_UID:
            raise exceptions.DuplicateUIDsInPriceListError('duplicate uids in price list')
        PURCHASES_BY_UID[purchase.uid] = purchase
