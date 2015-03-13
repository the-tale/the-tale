# coding: utf-8

from the_tale.accounts.payments import goods
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments import relations
from the_tale.accounts.payments.conf import payments_settings

PREMIUM_DAYS_DESCRIPTION = u'''
<p>
Подписка даёт следующие преимущества:
</p>

<ul>
  <li>герой получает на 50% больше опыта;</li>
  <li>максимальное количество энергии увеличивается на 50%;</li>
  <li>задания, выполняемые героями, начинают оказывать влияние на мир игры;</li>
  <li>игроки получают возможность голосовать за законы других игроков;</li>
  <li>герой сохраняет скорость получения опыта при длительном отсутствии игрока в игре.</li>
</ul>
'''

CARDS_DESCRIPTION = u'''
<p>
Карты судьбы — это особые одноразовые действия, позволяющие Хранителю оказать существенное влияние на героя или мир. Некоторые из них можно купить в магазине.
</p>
'''

ENERGY_CHARGES_DESCRIPTION = u'''
<p>
Количество дополнительной энергии не ограничено.<br/>
Вы можете использовать её, когда закончится запас энергии полученной от героя.<br/>
Всегда удобно иметь небольшой запас энергии на случай смерти героя или необходимости помочь ему в бою.
</p>
'''

PREFERENCES_DESCRIPTION = u'''
<p>
У каждого героя есть предпочтения, в соответствии с которыми он строит своё поведение.<br/>
Они доступны не сразу, а открываются с ростом уровня.<br/>
Вы можете не ждать и получить доступ к любому из них за небольшое количество печенек.
</p>
'''

GUILDS_DESCRIPTION = u'''
<p>
Гильдии — это объединения игроков, преследующих одну и ту же цель и желающих согласовывать свои действия в Пандоре.<br/>
Создать гильдию может любой игрок, если у него достаточно могущества.<br/>
Если Ваше могущество меньше, Вы можете купить разрешение на владение гильдией.
</p>
'''

RANDOM_PREMIUM_CHEST_DESCRIPTION = u'''
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
''' % {'gifts': '\n'.join(u'<li>%s</li>' % reward.description
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

def permanent_permission_purchase(uid, purchase_type, cost):
    return permanent_purchase(uid=uid,
                              purchase_type=purchase_type,
                              cost=cost,
                              transaction_description=u'Снятие ограничения уровня на предпочтение героя «%s»' % purchase_type.preference_type.text)


def card_purchase(uid, card_type, count, cost):
    from the_tale.game.cards.prototypes import CARDS
    return goods.Cards(uid=u'%s-%d' % (uid, count),
                       cost=cost,
                       card_type=card_type,
                       count=count,
                       name=card_type.text,
                       tooltip=CARDS[card_type].DESCRIPTION,
                       description=u'Покупка карты судьбы «%s» (%d шт.).' % (card_type.text, count),
                       transaction_description=u'Покупка карты судьбы «%s» (%d шт.).' % (card_type.text, count))


RANDOM_PREMIUM_CHEST = goods.PurchaseGroup(type=relations.GOODS_GROUP.CHEST,
                                           name=u'Делай добро и дари подписку!',
                                           short_name=u'Сделать добро',
                                           description=RANDOM_PREMIUM_CHEST_DESCRIPTION,
                                           items=[ goods.RandomPremiumChest(uid='random-premium-chest',
                                                                            cost=200,
                                                                            description=RANDOM_PREMIUM_CHEST_DESCRIPTION,
                                                                            name=u'Сделать добро',
                                                                            full_name=u'Делай добро и дари подписку!',
                                                                            transaction_description=u'Подписка в подарок случайному игроку') ])


PRICE_GROUPS = [RANDOM_PREMIUM_CHEST,

                goods.PurchaseGroup(type=relations.GOODS_GROUP.PREMIUM,
                                    name=u'Подписка',
                                    description=PREMIUM_DAYS_DESCRIPTION,
                                    items=[ goods.PremiumDays(uid=u'subscription-15',
                                                              name=u'15 дней',
                                                              full_name=u'15 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=180,
                                                              days=15,
                                                              transaction_description=u'Продление подписки на 15 дней.'),

                                            goods.PremiumDays(uid=u'subscription-30',
                                                              name=u'30 дней',
                                                              full_name=u'30 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=300,
                                                              days=30,
                                                              transaction_description=u'Продление подписки на 30 дней.'),

                                            goods.PremiumDays(uid=u'subscription-90',
                                                              name=u'90 дней',
                                                              full_name=u'90 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=750,
                                                              days=90,
                                                              transaction_description=u'Продление подписки на 90 дней.'),

                                            permanent_purchase(uid=u'subscription-infinit',
                                                               purchase_type=relations.PERMANENT_PURCHASE_TYPE.INFINIT_SUBSCRIPTION,
                                                               cost=6000,
                                                               transaction_description=u'Приобретение вечной подписки.')  ]),

                goods.PurchaseGroup(type=relations.GOODS_GROUP.ENERGY,
                                    name=u'Энергия',
                                    description=ENERGY_CHARGES_DESCRIPTION,
                                    items=[ goods.Energy(uid=u'energy-10',
                                                         name=u'10 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=10,
                                                         energy=10,
                                                         transaction_description=u'Покупка 10 единиц энергии.'),

                                            goods.Energy(uid=u'energy-100',
                                                         name=u'100 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=90,
                                                         energy=100,
                                                         transaction_description=u'Покупка 100 единиц энергии.'),

                                            goods.Energy(uid=u'energy-1000',
                                                         name=u'1000 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=850,
                                                         energy=1000,
                                                         transaction_description=u'Покупка 1000 единиц энергии.'),

                                            goods.Energy(uid=u'energy-10000',
                                                         name=u'10000 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=8000,
                                                         energy=10000,
                                                         transaction_description=u'Покупка 10000 единиц энергии.'),

                                                         ]),

                goods.PurchaseGroup(type=relations.GOODS_GROUP.PREFERENCES,
                                    name=u'Предпочтения',
                                    description=PREFERENCES_DESCRIPTION,
                                    items=[ permanent_permission_purchase(uid=u'preference-place',
                                                                          cost=10,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_PLACE),

                                            permanent_permission_purchase(uid=u'preference-mob',
                                                                          cost=20,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_MOB),

                                            permanent_permission_purchase(uid=u'preference-friend',
                                                                          cost=30,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_FRIEND),

                                            permanent_permission_purchase(uid=u'preference-archetype',
                                                                          cost=40,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_ARCHETYPE),

                                            permanent_permission_purchase(uid=u'preference-enemy',
                                                                          cost=50,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_ENEMY),

                                            permanent_permission_purchase(uid=u'preference-companion-dedication',
                                                                          cost=60,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_COMPANION_DEDICATION),

                                            permanent_permission_purchase(uid=u'preference-favorite-item',
                                                                          cost=70,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_FAVORITE_ITEM),

                                            permanent_permission_purchase(uid=u'preference-risk-level',
                                                                          cost=80,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_RISK_LEVEL),

                                            permanent_permission_purchase(uid=u'preference-equipment-slot',
                                                                          cost=90,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_EQUIPMENT_SLOT),

                                            permanent_permission_purchase(uid=u'preference-companion-empathy',
                                                                          cost=100,
                                                                          purchase_type=relations.PERMANENT_PURCHASE_TYPE.PREFERENCE_COMPANION_EMPATHY),
                                                                           ]),

                goods.PurchaseGroup(type=relations.GOODS_GROUP.CLANS,
                                    name=u'Гильдии',
                                    description=GUILDS_DESCRIPTION,
                                    items=[ permanent_purchase(uid=u'clan-ownership-right',
                                                               cost=150,
                                                               purchase_type=relations.PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT,
                                                               transaction_description=u'Приобретение разрешения на владение гильдией.') ]),
                ]


                # goods.PurchaseGroup(type=relations.GOODS_GROUP.CARDS,
                #                     name=u'Карты судьбы',
                #                     description=CARDS_DESCRIPTION,
                #                     items=[ card_purchase(uid='card-keepers-goods-',
                #                                           card_type=CARD_TYPE.KEEPERS_GOODS_LEGENDARY,
                #                                           count=1,
                #                                           cost=1000)])



PURCHASES_BY_UID = {}

for group in PRICE_GROUPS:
    for purchase in group.items:
        if purchase.uid in PURCHASES_BY_UID:
            raise exceptions.DuplicateUIDsInPriceListError('duplicate uids in price list')
        PURCHASES_BY_UID[purchase.uid] = purchase
