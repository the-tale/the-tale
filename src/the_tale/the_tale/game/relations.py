
from rels import Column
from rels.django import DjangoEnum

from pynames.relations import GENDER as PYNAMES_GENDER

from utg import relations as utg_relations

from the_tale.game.balance.power import  PowerDistribution
from the_tale.game.artifacts.relations import ARTIFACT_POWER_TYPE

from the_tale.game.balance import constants as c
from the_tale.game import technical_words

from the_tale.game.heroes import relations as heroes_relations


class GENDER(DjangoEnum):
    utg_id = Column()
    pynames_id = Column(unique=False)

    records = ( ('MASCULINE', 0, 'мужчина', utg_relations.GENDER.MASCULINE, PYNAMES_GENDER.MALE),
                ('FEMININE', 1, 'женщина', utg_relations.GENDER.FEMININE, PYNAMES_GENDER.FEMALE),
                ('NEUTER', 2, 'оно', utg_relations.GENDER.NEUTER, PYNAMES_GENDER.MALE) )


def _race_linguistics_restrictions(race):
    def _linguistics_restrictions():
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage
        return [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.RACE, getattr(RACE, race).value)]
    return _linguistics_restrictions

class RACE(DjangoEnum):
    multiple_text = Column()
    male_text = Column()
    female_text = Column()
    utg_name_form = Column()
    linguistics_restrictions = Column()
    energy_regeneration = Column(related_name='base_race')

    records = ( ('HUMAN', 0, 'человек', 'люди', 'мужчина', 'женщина',
                 technical_words.RACE_HUMANS, _race_linguistics_restrictions('HUMAN'), heroes_relations.ENERGY_REGENERATION.PRAY),
                ('ELF', 1, 'эльф', 'эльфы', 'эльф', 'эльфийка',
                 technical_words.RACE_ELFS, _race_linguistics_restrictions('ELF'), heroes_relations.ENERGY_REGENERATION.INCENSE),
                ('ORC', 2, 'орк',  'орки', 'орк', 'оркесса',
                 technical_words.RACE_ORCS, _race_linguistics_restrictions('ORC'), heroes_relations.ENERGY_REGENERATION.SACRIFICE),
                ('GOBLIN', 3, 'гоблин', 'гоблины', 'гоблин', 'гоблинша',
                 technical_words.RACE_GOBLINS, _race_linguistics_restrictions('GOBLIN'), heroes_relations.ENERGY_REGENERATION.MEDITATION),
                ('DWARF', 4, 'дварф', 'дварфы', 'дварф', 'дварфийка',
                 technical_words.RACE_DWARFS, _race_linguistics_restrictions('DWARF'), heroes_relations.ENERGY_REGENERATION.SYMBOLS) )


class GAME_STATE(DjangoEnum):

    records = ( ('STOPPED', 0, 'остановлена'),
                ('WORKING', 1, 'запущена')  )



class HABIT_INTERVAL(DjangoEnum):
    female_text = Column()
    neuter_text = Column()
    place_text = Column()
    left_border = Column()
    right_border = Column()


class HABIT_HONOR_INTERVAL(HABIT_INTERVAL):
    records = ( ('LEFT_3', 0, 'бесчестный', 'бесчестная', 'бесчестное', 'криминальная столица', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, 'подлый', 'подлая', 'подлое', 'бандитская вотчина', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, 'порочный', 'порочная', 'порочное', 'неблагополучный город', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, 'себе на уме', 'себе на уме', 'себе на уме', 'обычный город', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, 'порядочный', 'порядочная', 'порядочное', 'благополучное поселение', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, 'благородный', 'благородная', 'благородное', 'честный город', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, 'хозяин своего слова', 'хозяйка своего слова', 'хозяин своего слова', 'оплот благородства', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER) )


class HABIT_PEACEFULNESS_INTERVAL(HABIT_INTERVAL):
    records = ( ('LEFT_3', 0, 'скорый на расправу', 'скорая на расправу', 'скорое на расправу', 'территория вендетт', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, 'вспыльчивый', 'вспыльчивая', 'вспыльчивое', 'пристанище горячих голов', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, 'задира', 'задира', 'задира', 'беспокойное место', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, 'сдержанный', 'сдержанная', 'сдержаное', 'неприметное поселение', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, 'доброхот', 'доброхот', 'доброхот', 'спокойное место', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, 'миролюбивый', 'миролюбивая', 'миролюбивое', 'мирное поселение', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, 'гуманист', 'гуманист', 'гуманист', 'центр цивилизации', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER) )


class HABIT_TYPE(DjangoEnum):
    intervals = Column()
    plural_accusative = Column()
    verbose_value = Column()

    records = ( ('HONOR', 0, 'честь', HABIT_HONOR_INTERVAL, 'чести', 'honor'),
                ('PEACEFULNESS', 1, 'миролюбие', HABIT_PEACEFULNESS_INTERVAL, 'миролюбия', 'peacefulness') )


class ARCHETYPE(DjangoEnum):
    power_distribution = Column()
    description = Column()
    allowed_power_types = Column(no_index=True, unique=False)

    records = (('MAGICAL', 0, 'маг', PowerDistribution(0.25, 0.75), 'герой предпочитает магию грубой силе', [ARTIFACT_POWER_TYPE.MOST_MAGICAL,
                                                                                                             ARTIFACT_POWER_TYPE.MAGICAL,
                                                                                                             ARTIFACT_POWER_TYPE.NEUTRAL]),
               ('NEUTRAL', 1, 'авантюрист', PowerDistribution(0.5, 0.5), 'герой соблюдает баланс между мечом и магией', [ARTIFACT_POWER_TYPE.MAGICAL,
                                                                                                                         ARTIFACT_POWER_TYPE.NEUTRAL,
                                                                                                                         ARTIFACT_POWER_TYPE.PHYSICAL]),
               ('PHYSICAL', 2, 'воин', PowerDistribution(0.75, 0.25), 'герой полагается на воинские умения', [ARTIFACT_POWER_TYPE.NEUTRAL,
                                                                                                              ARTIFACT_POWER_TYPE.PHYSICAL,
                                                                                                              ARTIFACT_POWER_TYPE.MOST_PHYSICAL]))


class SUPERVISOR_TASK_TYPE(DjangoEnum):
    records = (('ARENA_PVP_1X1', 0, 'создать pvp бой на арене'),)

class SUPERVISOR_TASK_STATE(DjangoEnum):
    records = ( ('WAITING', 0, 'ожидает ресурсы'),
                ('PROCESSED', 1, 'обработана'),
                ('ERROR', 2, 'ошибка при обработке'), )

class COMMUNICATION_VERBAL(DjangoEnum):
    records = ( ('CAN_NOT', 0, 'не может'),
                ('CAN', 1, 'может'), )

class COMMUNICATION_GESTURES(DjangoEnum):
    records = ( ('CAN_NOT', 0, 'не может'),
                ('CAN', 1, 'может'), )

class COMMUNICATION_TELEPATHIC(DjangoEnum):
    records = ( ('CAN_NOT', 0, 'не может'),
                ('CAN', 1, 'может'), )

class INTELLECT_LEVEL(DjangoEnum):
    records = ( ('NONE', 0, 'отсутствует'),
                ('REFLEXES', 1, 'рефлексы'),
                ('INSTINCTS', 2, 'инстинкты'),
                ('LOW', 3, 'низкий'),
                ('NORMAL', 4, 'нормальный'),
                ('HIGHT', 5, 'гений') )

class ACTOR(DjangoEnum):
    records = ( ('HERO', 0, 'герой'),
                ('MOB', 1, 'монстр'),
                ('PERSON', 2, 'Мастер'),
                ('COMPANION', 3, 'спутник')  )


class BEING_TYPE(DjangoEnum):
    companion_heal_modifier = Column(unique=False)
    companion_coherence_modifier = Column(unique=False)

    records = ( ('PLANT', 0, 'растения', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
                ('ANIMAL', 1, 'животные', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
                ('SUPERNATURAL', 2, 'стихийные существа', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
                ('MECHANICAL', 3, 'конструкты', heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL, heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED),
                # (u'BARBARIAN', 4, u'дикари', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
                ('CIVILIZED', 5, 'разумные двуногие', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
                ('COLDBLOODED', 6, 'хладнокровные гады', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
                ('INSECT', 7, 'насекомые', heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL, heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED),
                ('DEMON', 8, 'демоны', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
                ('UNDEAD', 9, 'нежить', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
                ('MONSTER', 10, 'чудовища', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED),
                ('CHIMERA', 11, 'химеры', heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL, heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED) )
