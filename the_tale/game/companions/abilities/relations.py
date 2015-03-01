# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

class METATYPE(DjangoEnum):
    description = Column()

    records = ( (u'TRAVEL', 0, u'дорожная', u'влияет на скорость путешествия героя'),
                (u'BATTLE', 1, u'боевая', u'влияет на битвы'),
                (u'MONEY', 2, u'денежная', u'влияет на деньги и предметы'),
                (u'OTHER', 3, u'необычная', u'имеет особый эффект'),
                (u'UNCHANGEBLE', 4, u'неизменная', u'оказывает постоянный эффект, независимо от других свойств спутника или героя') )

class EFFECT(DjangoEnum):
    metatype = Column(unique=False)

    records = ( (u'COHERENCE_SPEED', 0, u'скорость изменения слаженности', METATYPE.UNCHANGEBLE),
                (u'CHANGE_HABITS', 1, u'изменение характера', METATYPE.UNCHANGEBLE),
                (u'QUEST_MONEY_REWARD', 2, u'денежная награда за задание', METATYPE.MONEY),
                (u'MAX_BAG_SIZE', 3, u'максимальный размер рюкзака', METATYPE.UNCHANGEBLE),
                (u'POLITICS_POWER', 4, u'бонус к влиянию', METATYPE.OTHER),
                (u'MAGIC_DAMAGE_BONUS', 5, u'бонус к магическому урону героя', METATYPE.BATTLE),
                (u'PHYSIC_DAMAGE_BONUS', 6, u'бонус к физическому урону героя', METATYPE.BATTLE),
                (u'SPEED', 7, u'бонус к скорости движения героя', METATYPE.TRAVEL),

                (u'INITIATIVE', 9, u'инициатива', METATYPE.BATTLE),
                (u'BATTLE_PROBABILITY', 10, u'вероятность начала боя', METATYPE.TRAVEL),
                (u'LOOT_PROBABILITY', 11, u'вероятность получить добычу', METATYPE.BATTLE),
                (u'COMPANION_DAMAGE', 12, u'урон по спутнику', METATYPE.UNCHANGEBLE),
                (u'COMPANION_DAMAGE_PROBABILITY', 13, u'вероятность получить урон', METATYPE.BATTLE),
                (u'COMPANION_STEAL_MONEY', 14, u'спутник крадёт деньги', METATYPE.MONEY),
                (u'COMPANION_STEAL_ITEM', 15, u'спутник крадёт предметы', METATYPE.MONEY),
                (u'COMPANION_SPARE_PARTS', 16, u'спутник разваливается на дорогие запчасти', METATYPE.UNCHANGEBLE),
                (u'COMPANION_EXPERIENCE', 17, u'спутник так или иначе приносит опыт', METATYPE.OTHER),
                (u'COMPANION_DOUBLE_ENERGY_REGENERATION', 18, u'герой может восстновить в 2 раза больше энергии', METATYPE.OTHER),
                (u'COMPANION_REGENERATION', 19, u'спутник как-либо восстанавливает своё здоровье', METATYPE.OTHER),
                (u'COMPANION_EAT', 20, u'спутник требует покупки еды', METATYPE.MONEY),
                (u'COMPANION_EAT_DISCOUNT', 21, u'у спутника есть скидка на покупку еды', METATYPE.MONEY),
                (u'COMPANION_DRINK_ARTIFACT', 22, u'спутник пропивает артефакты при посещении города', METATYPE.MONEY),
                (u'COMPANION_EXORCIST', 23, u'спутник является экзорцистом', METATYPE.BATTLE),
                (u'REST_LENGTH', 24, u'изменение скорости лечения на отдыхе', METATYPE.TRAVEL),
                (u'IDLE_LENGTH', 25, u'изменение времени бездействия', METATYPE.TRAVEL),
                (u'COMPANION_BLOCK_PROBABILITY', 26, u'вероятность блока спутника', METATYPE.BATTLE),
                (u'HUCKSTER', 27, u'спутник даёт бонус к цене продажи и покупки', METATYPE.MONEY),
                (u'MIGHT_CRIT_CHANCE', 28, u'шанс критического срабатывания способности хранителя', METATYPE.OTHER),

                (u'BATTLE_ABILITY_HIT', 29, u'небольшое увеличение инициативы и способность удар', METATYPE.BATTLE),
                (u'BATTLE_ABILITY_STRONG_HIT', 30, u'небольшое увеличение инициативы и способность тяжёлый удар', METATYPE.BATTLE),
                (u'BATTLE_ABILITY_RUN_UP_PUSH', 31, u'небольшое увеличение инициативы и способность разбег-толчёк', METATYPE.BATTLE),
                (u'BATTLE_ABILITY_FIREBALL', 32, u'небольшое увеличение инициативы и способность огненный шар', METATYPE.BATTLE),
                (u'BATTLE_ABILITY_POSION_CLOUD', 33, u'небольшое увеличение инициативы и способность отравленное облако', METATYPE.BATTLE),
                (u'BATTLE_ABILITY_FREEZING', 34, u'небольшое увеличение инициативы и способность заморозка', METATYPE.BATTLE),

                (u'COMPANION_TELEPORTATION', 35, u'спутник как-либо перемещает героя в пути', METATYPE.TRAVEL),

                (u'DEATHY', 36, u'для смерти, распугивает всех', METATYPE.UNCHANGEBLE),

                (u'RARITY', 37, u'редкость', METATYPE.UNCHANGEBLE),

                (u'LEAVE_HERO', 38, u'покидает героя', METATYPE.UNCHANGEBLE),

                )


class FIELDS(DjangoEnum):
    common = Column(unique=False)

    records = ( ('COHERENCE_SPEED', 0, u'слаженность', False),
                ('HONOR', 1, u'честь', False),
                ('PEACEFULNESS', 2, u'миролюбие', False),
                ('START_1', 3, u'начальная 1', False),
                ('START_2', 4, u'начальная 2', False),
                ('START_3', 5, u'начальная 3', False),
                ('START_4', 6, u'начальная 4', False),
                ('START_5', 7, u'начальная 5', False),
                ('ABILITY_1', 8, u'способность 1', True),
                ('ABILITY_2', 9, u'способность 2', True),
                ('ABILITY_3', 10, u'способность 3', True),
                ('ABILITY_4', 11, u'способность 4', True),
                ('ABILITY_5', 12, u'способность 5', True),
                ('ABILITY_6', 13, u'способность 6', True),
                ('ABILITY_7', 14, u'способность 7', True),
                ('ABILITY_8', 15, u'способность 8', True),
                ('ABILITY_9', 16, u'способность 9', True) )
