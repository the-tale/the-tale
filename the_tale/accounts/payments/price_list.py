# coding: utf-8

from the_tale.accounts.payments.goods import PremiumDays, PermanentPurchase, EnergyCharges, ResetHeroPreference, ResetHeroAbilities, RechooseHeroAbilitiesChoices
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments.relations import PERMANENT_PURCHASE_TYPE

from the_tale.game.heroes.relations import PREFERENCE_TYPE


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

def reset_hero_preference(uid, preference_type, cost):
    return ResetHeroPreference(uid=uid,
                               preference_type=preference_type,
                               cost=cost,
                               description=u'Сброс предпочтения героя: «%s» (вместо сброшенного предпочтения сразу можно выбрать новое)' % preference_type.text,
                               name=u'Сброс предпочтения героя: «%s»' % preference_type.text,
                               transaction_description=u'Сброс предпочтения героя: «%s»' % preference_type.text)


rechoose_hero_abilities = RechooseHeroAbilitiesChoices(uid='hero-abilities-rechoose-choices',
                                                       cost=50,
                                                       description=u'Изменяет список новых способностей, доступных герою для выбора. Гарантируется, что как минимум одна способность в новом списке будет отличаться от старого.',
                                                       name=u'Изменение списка новых способностей героя',
                                                       transaction_description=u'Изменение списка новых способностей героя')


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

                EnergyCharges(uid=u'energy-charge-100',
                              name=u'100 зарядов энергии',
                              description=ENERGY_CHARGES_DESCRIPTION,
                              cost=700,
                              charges_number=100,
                              transaction_description=u'Покупка 100 зарядов энергии.'),

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
                                   transaction_description=u'Приобретение разрешения на владение гильдией.'),

                reset_hero_preference(uid='hero-preference-reset-mob', preference_type=PREFERENCE_TYPE.MOB, cost=10),
                reset_hero_preference(uid='hero-preference-reset-place', preference_type=PREFERENCE_TYPE.PLACE, cost=50),
                reset_hero_preference(uid='hero-preference-reset-friend', preference_type=PREFERENCE_TYPE.FRIEND, cost=75),
                reset_hero_preference(uid='hero-preference-reset-enemy', preference_type=PREFERENCE_TYPE.ENEMY, cost=100),
                reset_hero_preference(uid='hero-preference-reset-energy-regeneration-type', preference_type=PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, cost=10),
                reset_hero_preference(uid='hero-preference-reset-equipment-slot', preference_type=PREFERENCE_TYPE.EQUIPMENT_SLOT, cost=25),
                reset_hero_preference(uid='hero-preference-reset-risk-level', preference_type=PREFERENCE_TYPE.RISK_LEVEL, cost=10),
                reset_hero_preference(uid='hero-preference-reset-favorite-item', preference_type=PREFERENCE_TYPE.FAVORITE_ITEM, cost=25),

                ResetHeroAbilities(uid='hero-abilities-reset',
                                   cost=300,
                                   description=u'Сброс способностей героя (после сброса сразу можно выбрать новые способности)',
                                   name=u'Сброс способностей героя',
                                   transaction_description=u'Сброс способностей героя'),

                rechoose_hero_abilities ]


PURCHASES_BY_UID = {purchase.uid:purchase for purchase in PRICE_LIST}

if len(PURCHASES_BY_UID) != len(PRICE_LIST):
    raise exceptions.DuplicateUIDsInPriceListError('duplicate uids in price list')
