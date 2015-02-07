# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class EFFECT(DjangoEnum):
    records = ( (u'COHERENCE_SPEED', 0, u'скорость изменения слаженности'),
                (u'CHANGE_HABITS', 1, u'изменение характера'),
                (u'QUEST_MONEY_REWARD', 2, u'денежная награда за задание'),
                (u'MAX_BAG_SIZE', 3, u'максимальный размер рюкзака'),
                (u'POLITICS_POWER', 4, u'бонус к влиянию'),
                (u'MAGIC_DAMAGE_BONUS', 5, u'бонус к магическому урону героя'),
                (u'PHYSIC_DAMAGE_BONUS', 6, u'бонус к физическому урону героя'),
                (u'SPEED', 7, u'бонус к скорости движения героя'),

                (u'INITIATIVE', 9, u'инициатива'),
                (u'BATTLE_PROBABILITY', 10, u'вероятность начала боя'),
                (u'LOOT_PROBABILITY', 11, u'вероятность получить добычу'),
                (u'COMPANION_DAMAGE', 12, u'урон по спутнику'),
                (u'COMPANION_DAMAGE_PROBABILITY', 13, u'вероятность получить урон'),
                (u'COMPANION_STEAL_MONEY', 14, u'спутник крадёт деньги'),
                (u'COMPANION_STEAL_ITEM', 15, u'спутник крадёт предметы'),
                (u'COMPANION_SPARE_PARTS', 16, u'спутник разваливается на дорогие запчасти'),
                (u'COMPANION_EXPERIENCE', 17, u'спутник так или иначе приносит опыт'),
                (u'COMPANION_DOUBLE_ENERGY_REGENERATION', 18, u'герой может восстновить в 2 раза больше энергии'),
                (u'COMPANION_REGENERATION', 19, u'спутник как-либо восстанавливает своё здоровье'),
                (u'COMPANION_EAT', 20, u'спутник требует покупки еды'),
                (u'COMPANION_EAT_DISCOUNT', 21, u'у спутника есть скидка на покупку еды'),
                (u'COMPANION_DRINK_ARTIFACT', 22, u'спутник пропивает артефакты при посещении города'),
                (u'COMPANION_EXORCIST', 23, u'спутник является экзорцистом'),
                (u'REST_LENGTH', 24, u'изменение скорости лечения на отдыхе'),
                (u'IDLE_LENGTH', 25, u'изменение времени бездействия'),
                (u'COMPANION_BLOCK_PROBABILITY', 26, u'вероятность блока спутника'),
                (u'HUCKSTER', 27, u'спутник даёт бонус к цене продажи и покупки'),
                (u'MIGHT_CRIT_CHANCE', 28, u'шанс критического срабатывания способности хранителя'),

                (u'BATTLE_ABILITY_HIT', 29, u'небольшое увеличение инициативы и способность удар'),
                (u'BATTLE_ABILITY_STRONG_HIT', 30, u'небольшое увеличение инициативы и способность тяжёлый удар'),
                (u'BATTLE_ABILITY_RUN_UP_PUSH', 31, u'небольшое увеличение инициативы и способность разбег-толчёк'),
                (u'BATTLE_ABILITY_FIREBALL', 32, u'небольшое увеличение инициативы и способность огненный шар'),
                (u'BATTLE_ABILITY_POSION_CLOUD', 33, u'небольшое увеличение инициативы и способность отравленное облако'),
                (u'BATTLE_ABILITY_FREEZING', 34, u'небольшое увеличение инициативы и способность заморозка'),

                (u'COMPANION_TELEPORTATION', 35, u'спутник как-либо перемещает героя в пути')

                )


class FIELDS(DjangoEnum):
    common = Column(unique=False)

    records = ( ('COHERENCE_SPEED', 0, u'слаженность', False),
                ('HONOR', 1, u'честь', False),
                ('PEACEFULNESS', 2, u'миролюбие', False),
                ('START_1', 3, u'начальная 1', False),
                ('START_2', 4, u'начальная 2', False),
                ('START_3', 5, u'начальная 3', False),
                ('ABILITY_1', 6, u'способность 1', True),
                ('ABILITY_2', 7, u'способность 2', True),
                ('ABILITY_3', 8, u'способность 3', True),
                ('ABILITY_4', 9, u'способность 4', True),
                ('ABILITY_5', 10, u'способность 5', True),
                ('ABILITY_6', 11, u'способность 6', True),
                ('ABILITY_7', 12, u'способность 7', True),
                ('ABILITY_8', 13, u'способность 8', True),
                ('ABILITY_9', 14, u'способность 9', True) )
