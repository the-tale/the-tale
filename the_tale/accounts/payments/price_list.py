# coding: utf-8

from accounts.payments.goods import PremiumDays, PermanentPurchase, EnergyCharges
from accounts.payments import exceptions
from accounts.payments.relations import PERMANENT_PURCHASE_TYPE


PREMIUM_DAYS_DESCRIPTION = u'''
<p>
Подписка даёт следующие преимущества:
</p>

<ul>
  <li>герой получает на 50% больше опыта;</li>
  <li>максимальное количество энергии увеличивается на 50%;</li>
  <li>задания, выполняемые героями, начинают оказывать влияние на мир игры;</li>
  <li>игроки получают возможность участвовать в политике (выдвигать законы и голосовать за них);</li>
  <li>герой сохраняет скорость получения опыта при длительном отсутствии игрока в игре.</li>
</ul>
'''

ENERGY_CHARGES_DESCRIPTION = u'''
<p>
С помощью заряда энергии Вы можете полностью восстановить свой запас энергии. Заряды накапливаются, поэтому можно купить сразу несколько, чтобы использовать по мере необходимости.
</p>
'''


def permanent_purchase(uid, purchase_type, cost, transaction_description):
    return PermanentPurchase(uid=uid,
                             name=purchase_type.text,
                             description=purchase_type.description,
                             cost=cost,
                             purchase_type=purchase_type,
                             transaction_description=transaction_description)

def permanent_permission_purchase(uid, purchase_type, cost):
    return permanent_purchase(uid=uid,
                              purchase_type=purchase_type,
                              cost=cost,
                              transaction_description=u'Снятие ограничения уровня на предпочтение героя «%s»' % purchase_type.preference_type.text)


PRICE_LIST = [  PremiumDays(uid=u'subscription-7',
                            name=u'7 дней подписки',
                            description=PREMIUM_DAYS_DESCRIPTION,
                            cost=100,
                            days=7,
                            transaction_description=u'Продление подписки на 7 дней.'),

                PremiumDays(uid=u'subscription-15',
                            name=u'15 дней подписки',
                            description=PREMIUM_DAYS_DESCRIPTION,
                            cost=180,
                            days=15,
                            transaction_description=u'Продление подписки на 15 дней.'),

                PremiumDays(uid=u'subscription-30',
                            name=u'30 дней подписки',
                            description=PREMIUM_DAYS_DESCRIPTION,
                            cost=300,
                            days=30,
                            transaction_description=u'Продление подписки на 30 дней.'),

                PremiumDays(uid=u'subscription-90',
                            name=u'90 дней подписки',
                            description=PREMIUM_DAYS_DESCRIPTION,
                            cost=750,
                            days=90,
                            transaction_description=u'Продление подписки на 90 дней.'),

                EnergyCharges(uid=u'energy-charge-1',
                              name=u'1 заряд энергии',
                              description=ENERGY_CHARGES_DESCRIPTION,
                              cost=10,
                              charges_number=1,
                              transaction_description=u'Покупка одного заряда энергии.'),

                EnergyCharges(uid=u'energy-charge-10',
                              name=u'10 зарядов энергии',
                              description=ENERGY_CHARGES_DESCRIPTION,
                              cost=80,
                              charges_number=10,
                              transaction_description=u'Покупка 10 зарядов энергии.'),

                permanent_permission_purchase(uid=u'preference-place',
                                              cost=10,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_PLACE),

                permanent_permission_purchase(uid=u'preference-risk-level',
                                              cost=20,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_RISK_LEVEL),

                permanent_permission_purchase(uid=u'preference-friend',
                                              cost=30,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_FRIEND),

                permanent_permission_purchase(uid=u'preference-favorite-item',
                                              cost=40,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_FAVORITE_ITEM),

                permanent_permission_purchase(uid=u'preference-enemy',
                                              cost=50,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_ENEMY),

                permanent_permission_purchase(uid=u'preference-equipment-slot',
                                              cost=60,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_EQUIPMENT_SLOT),

                permanent_permission_purchase(uid=u'preference-mob',
                                              cost=70,
                                              purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_MOB),

                permanent_purchase(uid=u'clan-ownership-right',
                                   cost=150,
                                   purchase_type=PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT,
                                   transaction_description=u'Приобретение разрешения на владение гильдией.')]

PURCHASES_BY_UID = {purchase.uid:purchase for purchase in PRICE_LIST}

if len(PURCHASES_BY_UID) != len(PRICE_LIST):
    raise exceptions.DuplicateUIDsInPriceListError('duplicate uids in price list')
