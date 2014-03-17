# coding: utf-8

from the_tale.accounts.payments import goods
from the_tale.accounts.payments import exceptions
from the_tale.accounts.payments.relations import PERMANENT_PURCHASE_TYPE

from the_tale.game.heroes.relations import PREFERENCE_TYPE, HABIT_TYPE


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

PREFERENCES_RESET_DESCRIPTION = u'''
<p>
Вы можете сбросить любое предпочтение героя, независимо от задержки на его изменение в игре.
</p>
'''

HABITS_DESCRIPTION = u'''
<p>
Каждый герой обладает набором черт, определяющих его подход к жизни.<br/>
Черты постепенно изменяются, в зависимости от действий героя и игрока.<br/>
Вы можете ускорить их изменение, купив очки нужной черты.
</p>
'''

ABILITIES_DESCRIPTION = u'''
<p>
Раз в несколько уровней герой получает возможность выучить новое умение, способное облегчить его жизнь.<br/>
При этом нельзя выбрать любое умение — каждый раз герою предлагается на выбор лишь несколько из них.<br/>
Однако, потратив печеньки, Вы можете изменить список предлагаемых способностей или сбросить все способности героя.
</p>
'''

GUILDS_DESCRIPTION = u'''
<p>
Гильдии — это объединения игроков, преследующих одну и ту же цель и желающих согласовывать свои действия в Пандоре.<br/>
Создать гильдию может любой игрок, если него достаточно могущества.<br/>
Если Ваше могущество меньше, Вы можете купить разрешение на владение гильдией.
</p>
'''

HABIT_MINOR_COST = 200
HABIT_MAJOR_COST = 450

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

def reset_hero_preference(uid, preference_type, cost):
    return goods.ResetHeroPreference(uid=uid,
                                     preference_type=preference_type,
                                     cost=cost,
                                     description=u'Сброс предпочтения героя: «%s» (вместо сброшенного предпочтения сразу можно выбрать новое)' % preference_type.text,
                                     name=preference_type.text,
                                     full_name=u'Сброс предпочтения "%s"' % preference_type.text,
                                     transaction_description=u'Сброс предпочтения героя: «%s»' % preference_type.text)


rechoose_hero_abilities = goods.RechooseHeroAbilitiesChoices(uid='hero-abilities-rechoose-choices',
                                                       cost=50,
                                                       description=u'Изменяет список новых способностей, доступных герою для выбора. Гарантируется, что как минимум одна способность в новом списке будет отличаться от старого.',
                                                       name=u'Изменение списка новых способностей',
                                                       transaction_description=u'Изменение списка новых способностей героя')


def change_hero_habits(habit, value, cost):

    if habit.is_HONOR:
        name = u'%s чести' % value
        transaction_description = u'Покупка %s очков чести' % value

    elif habit.is_PEACEFULNESS:
        name = u'%s миролюбия' % value
        transaction_description = u'Покупка %s очков миролюбия' % value

    else:
        raise exceptions.UnknownHabit(habit=habit)

    return goods.ChangeHeroHabits(uid='hero-habits-%s-%d' % (habit.name.lower(), value),
                                  cost=cost,
                                  description=u'Мгновенное изменение очков черт героя на указанную величину',
                                  name=name,
                                  transaction_description=transaction_description,
                                  habit_type=habit,
                                  habit_value=value)


PRICE_GROUPS = [goods.PurchaseGroup(uid='subscription',
                                    name=u'Подписка',
                                    description=PREMIUM_DAYS_DESCRIPTION,
                                    items=[ goods.PremiumDays(uid=u'subscription-90',
                                                              name=u'90 дней',
                                                              full_name=u'90 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=750,
                                                              days=90,
                                                              transaction_description=u'Продление подписки на 90 дней.'),

                                            goods.PremiumDays(uid=u'subscription-30',
                                                              name=u'30 дней',
                                                              full_name=u'30 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=300,
                                                              days=30,
                                                              transaction_description=u'Продление подписки на 30 дней.'),

                                            goods.PremiumDays(uid=u'subscription-15',
                                                              name=u'15 дней',
                                                              full_name=u'15 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=180,
                                                              days=15,
                                                              transaction_description=u'Продление подписки на 15 дней.'),

                                            goods.PremiumDays(uid=u'subscription-7',
                                                              name=u'7 дней',
                                                              full_name=u'7 дней подписки',
                                                              description=PREMIUM_DAYS_DESCRIPTION,
                                                              cost=100,
                                                              days=7,
                                                              transaction_description=u'Продление подписки на 7 дней.') ]),
                goods.PurchaseGroup(uid='energy',
                                    name=u'Энергия',
                                    description=ENERGY_CHARGES_DESCRIPTION,
                                    items=[ goods.Energy(uid=u'energy-2000',
                                                         name=u'2000 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=700,
                                                         energy=2000,
                                                         transaction_description=u'Покупка 2000 единиц энергии.'),

                                            goods.Energy(uid=u'energy-200',
                                                         name=u'200 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=80,
                                                         energy=200,
                                                         transaction_description=u'Покупка 200 единиц энергии.'),

                                            goods.Energy(uid=u'energy-20',
                                                         name=u'20 энергии',
                                                         description=ENERGY_CHARGES_DESCRIPTION,
                                                         cost=10,
                                                         energy=20,
                                                         transaction_description=u'Покупка 20 единиц энергии.')
                                                         ]),

                goods.PurchaseGroup(uid='preference',
                                    name=u'Предпочтения',
                                    description=PREFERENCES_DESCRIPTION,
                                    items=[ permanent_permission_purchase(uid=u'preference-place',
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
                                                                          purchase_type=PERMANENT_PURCHASE_TYPE.PREFERENCE_MOB) ]),


                goods.PurchaseGroup(uid='preference-reset',
                                    name=u'Сброс предпочтений',
                                    description=PREFERENCES_RESET_DESCRIPTION,
                                    items=[ reset_hero_preference(uid='hero-preference-reset-mob', preference_type=PREFERENCE_TYPE.MOB, cost=10),
                                            reset_hero_preference(uid='hero-preference-reset-place', preference_type=PREFERENCE_TYPE.PLACE, cost=50),
                                            reset_hero_preference(uid='hero-preference-reset-friend', preference_type=PREFERENCE_TYPE.FRIEND, cost=75),
                                            reset_hero_preference(uid='hero-preference-reset-enemy', preference_type=PREFERENCE_TYPE.ENEMY, cost=100),
                                            reset_hero_preference(uid='hero-preference-reset-energy-regeneration-type', preference_type=PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, cost=10),
                                            reset_hero_preference(uid='hero-preference-reset-equipment-slot', preference_type=PREFERENCE_TYPE.EQUIPMENT_SLOT, cost=25),
                                            reset_hero_preference(uid='hero-preference-reset-risk-level', preference_type=PREFERENCE_TYPE.RISK_LEVEL, cost=10),
                                            reset_hero_preference(uid='hero-preference-reset-favorite-item', preference_type=PREFERENCE_TYPE.FAVORITE_ITEM, cost=25)]),

                goods.PurchaseGroup(uid='habits',
                                    name=u'Черты',
                                    description=HABITS_DESCRIPTION,
                                    items=[ change_hero_habits(habit=HABIT_TYPE.HONOR, value=1000, cost=HABIT_MAJOR_COST),
                                            change_hero_habits(habit=HABIT_TYPE.HONOR, value=-1000, cost=HABIT_MAJOR_COST),
                                            change_hero_habits(habit=HABIT_TYPE.HONOR, value=250, cost=HABIT_MINOR_COST),
                                            change_hero_habits(habit=HABIT_TYPE.HONOR, value=-250, cost=HABIT_MINOR_COST),

                                            change_hero_habits(habit=HABIT_TYPE.PEACEFULNESS, value=1000, cost=HABIT_MAJOR_COST),
                                            change_hero_habits(habit=HABIT_TYPE.PEACEFULNESS, value=-1000, cost=HABIT_MAJOR_COST),
                                            change_hero_habits(habit=HABIT_TYPE.PEACEFULNESS, value=250, cost=HABIT_MINOR_COST),
                                            change_hero_habits(habit=HABIT_TYPE.PEACEFULNESS, value=-250, cost=HABIT_MINOR_COST),]),

                goods.PurchaseGroup(uid='abilities',
                                    name=u'Способности',
                                    description=ABILITIES_DESCRIPTION,
                                    items=[ goods.ResetHeroAbilities(uid='hero-abilities-reset',
                                                                     cost=300,
                                                                     description=u'Сброс способностей героя (после сброса сразу можно выбрать новые способности)',
                                                                     name=u'Сброс способностей',
                                                                     transaction_description=u'Сброс способностей героя'),

                                            rechoose_hero_abilities ]),

                goods.PurchaseGroup(uid='clans',
                                    name=u'Гильдии',
                                    description=GUILDS_DESCRIPTION,
                                    items=[ permanent_purchase(uid=u'clan-ownership-right',
                                                               cost=150,
                                                               purchase_type=PERMANENT_PURCHASE_TYPE.CLAN_OWNERSHIP_RIGHT,
                                                               transaction_description=u'Приобретение разрешения на владение гильдией.') ])
                                                               ]


PURCHASES_BY_UID = {}

for group in PRICE_GROUPS:
    for purchase in group.items:
        if purchase.uid in PURCHASES_BY_UID:
            raise exceptions.DuplicateUIDsInPriceListError('duplicate uids in price list')
        PURCHASES_BY_UID[purchase.uid] = purchase
