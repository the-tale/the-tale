
import smart_imports

smart_imports.all()


class METATYPE(rels_django.DjangoEnum):
    description = rels.Column()

    records = (('TRAVEL', 0, 'дорожная', 'влияет на скорость путешествия героя'),
               ('BATTLE', 1, 'боевая', 'влияет на битвы'),
               ('MONEY', 2, 'денежная', 'влияет на деньги и предметы'),
               ('OTHER', 3, 'необычная', 'имеет особый эффект'),
               ('UNCHANGEBLE', 4, 'неизменная', 'оказывает постоянный эффект, независимо от других свойств спутника или героя'))


class EFFECT(rels_django.DjangoEnum):
    metatype = rels.Column(unique=False)

    records = (('COHERENCE_SPEED', 0, 'скорость изменения слаженности', METATYPE.UNCHANGEBLE),
               ('CHANGE_HABITS', 1, 'изменение характера', METATYPE.UNCHANGEBLE),
               ('QUEST_MONEY_REWARD', 2, 'денежная награда за задание', METATYPE.MONEY),
               ('MAX_BAG_SIZE', 3, 'максимальный размер рюкзака', METATYPE.UNCHANGEBLE),
               ('POLITICS_POWER', 4, 'бонус к влиянию', METATYPE.OTHER),
               ('MAGIC_DAMAGE_BONUS', 5, 'бонус к магическому урону героя', METATYPE.BATTLE),
               ('PHYSIC_DAMAGE_BONUS', 6, 'бонус к физическому урону героя', METATYPE.BATTLE),
               ('SPEED', 7, 'бонус к скорости движения героя', METATYPE.TRAVEL),

               ('INITIATIVE', 9, 'инициатива', METATYPE.BATTLE),
               ('BATTLE_PROBABILITY', 10, 'вероятность начала боя', METATYPE.TRAVEL),
               ('LOOT_PROBABILITY', 11, 'вероятность получить добычу', METATYPE.BATTLE),
               ('COMPANION_DAMAGE', 12, 'урон по спутнику', METATYPE.UNCHANGEBLE),
               ('COMPANION_DAMAGE_PROBABILITY', 13, 'вероятность получить урон', METATYPE.BATTLE),
               ('COMPANION_STEAL_MONEY', 14, 'спутник крадёт деньги', METATYPE.MONEY),
               ('COMPANION_STEAL_ITEM', 15, 'спутник крадёт предметы', METATYPE.MONEY),
               ('COMPANION_SPARE_PARTS', 16, 'спутник разваливается на дорогие запчасти', METATYPE.UNCHANGEBLE),
               ('COMPANION_EXPERIENCE', 17, 'спутник так или иначе приносит опыт', METATYPE.OTHER),
               ('COMPANION_DOUBLE_ENERGY_REGENERATION', 18, 'герой может восстновить в 2 раза больше энергии', METATYPE.OTHER),
               ('COMPANION_REGENERATION', 19, 'спутник как-либо восстанавливает своё здоровье', METATYPE.OTHER),
               ('COMPANION_EAT', 20, 'спутник требует покупки еды', METATYPE.MONEY),
               ('COMPANION_EAT_DISCOUNT', 21, 'у спутника есть скидка на покупку еды', METATYPE.MONEY),
               ('COMPANION_DRINK_ARTIFACT', 22, 'спутник пропивает артефакты при посещении города', METATYPE.MONEY),
               ('COMPANION_EXORCIST', 23, 'спутник является экзорцистом', METATYPE.BATTLE),
               ('REST_LENGTH', 24, 'изменение скорости лечения на отдыхе', METATYPE.TRAVEL),
               ('IDLE_LENGTH', 25, 'изменение времени бездействия', METATYPE.TRAVEL),
               ('COMPANION_BLOCK_PROBABILITY', 26, 'вероятность блока спутника', METATYPE.BATTLE),
               ('HUCKSTER', 27, 'спутник даёт бонус к цене продажи и покупки', METATYPE.MONEY),
               ('MIGHT_CRIT_CHANCE', 28, 'шанс критического срабатывания способности хранителя', METATYPE.OTHER),

               ('BATTLE_ABILITY_HIT', 29, 'небольшое увеличение инициативы и способность удар', METATYPE.BATTLE),
               ('BATTLE_ABILITY_STRONG_HIT', 30, 'небольшое увеличение инициативы и способность сильный удар', METATYPE.BATTLE),
               ('BATTLE_ABILITY_RUN_UP_PUSH', 31, 'небольшое увеличение инициативы и способность ошеломление', METATYPE.BATTLE),
               ('BATTLE_ABILITY_FIREBALL', 32, 'небольшое увеличение инициативы и способность пиромания', METATYPE.BATTLE),
               ('BATTLE_ABILITY_POSION_CLOUD', 33, 'небольшое увеличение инициативы и способность ядовитость', METATYPE.BATTLE),
               ('BATTLE_ABILITY_FREEZING', 34, 'небольшое увеличение инициативы и способность контроль', METATYPE.BATTLE),

               ('COMPANION_TELEPORTATION', 35, 'спутник как-либо перемещает героя в пути', METATYPE.TRAVEL),

               ('DEATHY', 36, 'для смерти, распугивает всех', METATYPE.UNCHANGEBLE),

               ('RARITY', 37, 'редкость', METATYPE.UNCHANGEBLE),

               ('LEAVE_HERO', 38, 'покидает героя', METATYPE.UNCHANGEBLE))


class FIELDS(rels_django.DjangoEnum):
    common = rels.Column(unique=False)

    records = (('COHERENCE_SPEED', 0, 'слаженность', False),
               ('HONOR', 1, 'честь', False),
               ('PEACEFULNESS', 2, 'миролюбие', False),
               ('START_1', 3, 'начальная 1', False),
               ('START_2', 4, 'начальная 2', False),
               ('START_3', 5, 'начальная 3', False),
               ('START_4', 6, 'начальная 4', False),
               ('START_5', 7, 'начальная 5', False),
               ('ABILITY_1', 8, 'способность 1', True),
               ('ABILITY_2', 9, 'способность 2', True),
               ('ABILITY_3', 10, 'способность 3', True),
               ('ABILITY_4', 11, 'способность 4', True),
               ('ABILITY_5', 12, 'способность 5', True),
               ('ABILITY_6', 13, 'способность 6', True),
               ('ABILITY_7', 14, 'способность 7', True),
               ('ABILITY_8', 15, 'способность 8', True),
               ('ABILITY_9', 16, 'способность 9', True))
