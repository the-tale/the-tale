# coding: utf-8

from accounts.payments.goods import PremiumDays, PermanentPurchase
from accounts.payments import exceptions
from accounts.payments.relations import PERMANENT_PURCHASE_TYPE


PREMIUM_DAYS_DESCRIPTION = u'''
<p>
Подписка на игру убирает штрафы, накладываемые на бесплатные аккаунты:
</p>

<ul>
  <li>задания, выполняемые героями, начинают оказывать влияние на мир игры;</li>
  <li>герои перестают получать штраф к опыту при длительном отсутствии игрока в игре;</li>
  <li>игроки получают возможность участвовать в политике (выдвигать законы и голосовать за них).</li>
</ul>
'''


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

                PermanentPurchase(uid=u'clan-ownership-right',
                                  name=PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT.text,
                                  description=PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT.description,
                                  cost=150,
                                  purchase_type=PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT,
                                  transaction_description=u'Приобретение разрешения на владение гильдией.')]

PURCHASES_BY_UID = {purchase.uid:purchase for purchase in PRICE_LIST}

if len(PURCHASES_BY_UID) != len(PRICE_LIST):
    raise exceptions.DuplicateUIDsInPriceListError('duplicate uids in price list')
