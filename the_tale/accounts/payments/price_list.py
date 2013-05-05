# coding: utf-8

from accounts.payments.goods import PremiumDays
from accounts.payments.exceptions import PayementsError


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


PRICE_LIST = [  PremiumDays(uid=u'subscription-30',
                            name=u'30 дней подписки',
                            description=PREMIUM_DAYS_DESCRIPTION,
                            cost=100,
                            days=30,
                            transaction_description=u'Продление подписки на 30 дней.'),

                PremiumDays(uid=u'subscription-90',
                            name=u'90 дней подписки',
                            description=PREMIUM_DAYS_DESCRIPTION,
                            cost=250,
                            days=90,
                            transaction_description=u'Продление подписки на 90 дней.') ]

PURCHASES_BY_UID = {purchase.uid:purchase for purchase in PRICE_LIST}

if len(PURCHASES_BY_UID) != len(PRICE_LIST):
    raise PayementsError('duplicate uids in price list')
