
from typing import ClassVar, Tuple

from rels import Column, Record
from rels.django import DjangoEnum

# TODO: remove
from the_tale.game.heroes import relations as heroes_relations


class COMMUNICATION_VERBAL(DjangoEnum):
    records = (('CAN_NOT', 0, 'не может'),
               ('CAN', 1, 'может'))


class COMMUNICATION_GESTURES(DjangoEnum):
    records = (('CAN_NOT', 0, 'не может'),
               ('CAN', 1, 'может'))


class COMMUNICATION_TELEPATHIC(DjangoEnum):
    records = (('CAN_NOT', 0, 'не может'),
               ('CAN', 1, 'может'))


class INTELLECT_LEVEL(DjangoEnum):
    records = (('NONE', 0, 'отсутствует'),
               ('REFLEXES', 1, 'рефлексы'),
               ('INSTINCTS', 2, 'инстинкты'),
               ('LOW', 3, 'низкий'),
               ('NORMAL', 4, 'нормальный'),
               ('HIGHT', 5, 'гений'))


class TYPE(DjangoEnum):
    companion_heal_modifier = Column(unique=False)
    companion_coherence_modifier = Column(unique=False)

    records = (('PLANT', 0, 'растения', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
               ('ANIMAL', 1, 'животные', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
               ('SUPERNATURAL', 2, 'стихийные существа', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
               ('MECHANICAL', 3, 'конструкты', heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL, heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED),
               # (u'BARBARIAN', 4, u'дикари', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
               ('CIVILIZED', 5, 'разумные двуногие', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
               ('COLDBLOODED', 6, 'хладнокровные гады', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
               ('INSECT', 7, 'насекомые', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
               ('DEMON', 8, 'демоны', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
               ('UNDEAD', 9, 'нежить', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
               ('MONSTER', 10, 'чудовища', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED))


class STRUCTURE(DjangoEnum):
    records = (('STRUCTURE_0', 0, 'глина'),
               ('STRUCTURE_1', 1, 'дерево'),
               ('STRUCTURE_2', 2, 'камень'),
               ('STRUCTURE_3', 3, 'металл'),
               ('STRUCTURE_4', 4, 'энергия'),
               ('STRUCTURE_5', 5, 'живая плоть'),
               ('STRUCTURE_6', 6, 'мёртвая плоть'),
               ('STRUCTURE_7', 7, 'плоть насекомого'),
               ('STRUCTURE_8', 8, 'бумага'))


class FEATURE(DjangoEnum):
    verbose_text = Column()
    allowed_for_hero = Column(unique=False)

    records = (('FEATURE_1', 1, 'борода: средняя', 'средняя борода', False),
               ('FEATURE_2', 2, 'глаза: много', 'много глаз', False),
               ('FEATURE_3', 3, 'глаза: один', 'единственный глаз', False),
               ('FEATURE_4', 4, 'глаза: остекленевшие (рыбьи)', 'остекленевшие глаза', False),
               ('FEATURE_5', 5, 'глаза: безумные', 'безумные глаза', False),
               ('FEATURE_6', 6, 'глаза: белые', 'белые глаза', False),
               ('FEATURE_7', 7, 'глаза: голубые', 'голубые глаза', False),
               ('FEATURE_8', 8, 'глаза: жёлтые', 'жёлтые глаза', False),
               ('FEATURE_9', 9, 'глаза: зелёные', 'зелёные глаза', False),
               ('FEATURE_10', 10, 'глаза: красные', 'красные глаза', False),
               ('FEATURE_11', 11, 'глаза: светятся', 'светящиеся глаза', False),
               ('FEATURE_12', 12, 'глаза: чёрные (без белков)', 'чёрные без белков глаза', False),
               ('FEATURE_13', 13, 'головы: 2', '2 головы', False),
               ('FEATURE_14', 14, 'головы: 3', '3 головы', False),
               ('FEATURE_15', 15, 'горбящийся', 'горбящийся', False),
               ('FEATURE_16', 16, 'грива', 'грива', False),
               ('FEATURE_17', 17, 'запах: гниль', 'пахнет гнилью', False),
               ('FEATURE_18', 18, 'запах: немытое тело (вонь)', 'воняет немытым телом', False),
               ('FEATURE_19', 19, 'запах: падаль', 'пахнет падалью', False),
               ('FEATURE_20', 20, 'заразный', 'заразный', False),
               ('FEATURE_21', 21, 'зубы: клыки', 'большие клыки', False),
               ('FEATURE_22', 22, 'кожа: кора', 'покрыт корой', False),
               ('FEATURE_23', 23, 'кожа: хитин', 'покрыт хитином', False),
               ('FEATURE_24', 24, 'кожа: чешуя', 'покрыт чешуёй', False),
               ('FEATURE_25', 25, 'кожа: маслянистая (блестящая)', 'покрыт блестящей маслянистой кожей', False),
               ('FEATURE_26', 26, 'кожа: бледная', 'бледная кожа', False),
               ('FEATURE_27', 27, 'кожа: морщинистая', 'морщинистая кожа', False),
               ('FEATURE_28', 28, 'кожа: ороговевшая', 'ороговевшая кожа', False),
               ('FEATURE_29', 29, 'кожа: тёмная', 'тёмная кожа', False),
               ('FEATURE_30', 30, 'крылья: перепончатые', 'перепончатые крылья', False),
               ('FEATURE_31', 31, 'крылья: пернатые', 'покрытые перьями крылья', False),
               ('FEATURE_32', 32, 'одежда: шкуры', 'одет в шкуры', False),
               ('FEATURE_33', 33, 'одежда: плохо', 'одет в плохую одежду', False),
               ('FEATURE_34', 34, 'одежда: хорошо', 'одет в хорошую одежду', False),
               ('FEATURE_35', 35, 'рога: большие', 'большие рога', False),
               ('FEATURE_36', 36, 'рога: маленькие', 'маленькие рожки', False),
               ('FEATURE_37', 37, 'руки: отсутствуют', 'нет рук', False),
               ('FEATURE_38', 38, 'руки: три', 'три руки', False),
               ('FEATURE_39', 39, 'тело: горит', 'горит огнём', False),
               ('FEATURE_40', 40, 'тело: светится', 'светится', False),
               ('FEATURE_41', 41, 'толстый', 'толстый', False),
               ('FEATURE_42', 42, 'торс: мощный', 'мощный торс', False),
               ('FEATURE_43', 43, 'торс: хилый', 'хилый торс', False),
               ('FEATURE_44', 44, 'красивый', 'красивый', False),
               ('FEATURE_45', 45, 'уродливый', 'уродливый', False),
               ('FEATURE_46', 46, 'хвост', 'хвост', False),
               ('FEATURE_47', 47, 'худой', 'худой', False),
               ('FEATURE_48', 48, 'шерсть: длинная', 'длинная шерсть', False),
               ('FEATURE_49', 49, 'шерсть: жёсткая', 'жёсткая шерсть', False),
               ('FEATURE_50', 50, 'шерсть: короткая', 'короткая шерсть', False),
               ('FEATURE_51', 51, 'шерсть: облезлая', 'облезлая шерсть', False),
               ('FEATURE_52', 52, 'шерсть: средней длины', 'шерсть средней длины', False),
               ('FEATURE_53', 53, 'крылья: каркасные', 'каркасные крылья', False),
               ('FEATURE_54', 54, 'крылья: бабочки', 'крылья как у бабочки', False))


class MOVEMENT(DjangoEnum):
    records = (('MOVEMENT_0', 0, '2 копыта'),
               ('MOVEMENT_1', 1, '2 лапы'),
               ('MOVEMENT_2', 2, '2 ноги'),
               ('MOVEMENT_3', 3, '4 копыта'),
               ('MOVEMENT_4', 4, '4 лапы'),
               ('MOVEMENT_5', 5, '6 лап'),
               ('MOVEMENT_6', 6, '8 лап'),
               ('MOVEMENT_7', 7, '16 лап'),
               ('MOVEMENT_8', 8, 'парит над землёй'),
               ('MOVEMENT_9', 9, 'ползает на корнях'),
               ('MOVEMENT_10', 10, 'ползает по змеиному'),
               ('MOVEMENT_11', 11, 'ездит на колёсах'),
               ('MOVEMENT_12', 12, 'перекатывается'))


class BODY(DjangoEnum):
    records = (('BODY_0', 0, 'бычье'),
               ('BODY_1', 1, 'гуманоидное'),
               ('BODY_2', 2, 'древоподобное'),
               ('BODY_3', 3, 'змеиное'),
               ('BODY_4', 4, 'конусовидное'),
               ('BODY_5', 5, 'кошачье'),
               ('BODY_6', 6, 'крысиное'),
               ('BODY_7', 7, 'лошадиное'),
               ('BODY_8', 8, 'медвежье'),
               ('BODY_9', 9, 'насекомоподобное'),
               ('BODY_10', 10, 'паучье'),
               ('BODY_11', 11, 'птичье'),
               ('BODY_12', 12, 'свиноподобное'),
               ('BODY_13', 13, 'сколопендроподобное'),
               ('BODY_14', 14, 'скорпионье'),
               ('BODY_15', 15, 'слизневое'),
               ('BODY_16', 16, 'собачье'),
               ('BODY_17', 17, 'сферическое'),
               ('BODY_18', 18, 'ящериное'),
               ('BODY_19', 19, 'бочкообразное'))


class SIZE(DjangoEnum):
    records = (('SIZE_0', 0, 'крохотный'),
               ('SIZE_1', 1, 'маленький'),
               ('SIZE_2', 2, 'средний'),
               ('SIZE_3', 3, 'большой'),
               ('SIZE_4', 4, 'огромный'),
               ('SIZE_5', 5, 'гигантский'))


class ORIENTATION(DjangoEnum):
    records = (('VERTICAL', 0, 'вертикальное'),
               ('HORIZONTAL', 1, 'горизонтальное'))


class AGE(DjangoEnum):
    records = (('YOUNG', 0, 'молодой'),
               ('MATURE', 1, 'зрелый'),
               ('OLD', 2, 'престарелый'))


class UPBRINGING(DjangoEnum):
    records = (('VULGAR', 0, 'уличное'),
               ('RURAL', 1, 'сельское'),
               ('PHILISTINE', 2, 'городское'),
               ('ARISTOCRATIC', 3, 'аристократическое'),
               ('PRIESTLY', 4, 'духовное'))


class FIRST_DEATH(DjangoEnum):
    records = (('ON_THE_SCAFFOLD', 0, 'на эшафоте'),
               ('IN_A_DRUNKEN_BRAWL', 1, 'в пьяной драке'),
               ('FROM_THE_MONSTER_FANGS', 2, 'от клыков монстра'),
               ('FROM_THE_DISEASE', 3, 'от болезни'),
               ('IN_A_SKIRMISH_WITH_THE_ROBBERS', 4, 'в стычке с разбойниками'))
