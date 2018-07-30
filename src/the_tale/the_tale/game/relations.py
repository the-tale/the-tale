
import smart_imports

smart_imports.all()


class GENDER(rels_django.DjangoEnum):
    utg_id = rels.Column()
    pynames_id = rels.Column(unique=False)

    records = (('MALE', 0, 'мужчина', utg_relations.GENDER.MASCULINE, pynames_relations.GENDER.MALE),
               ('FEMALE', 1, 'женщина', utg_relations.GENDER.FEMININE, pynames_relations.GENDER.FEMALE))


def _race_linguistics_restrictions(race):
    def _linguistics_restrictions():
        from the_tale.linguistics import restrictions as linguistics_restrictions
        return [linguistics_restrictions.get(getattr(RACE, race))]

    return _linguistics_restrictions


class RACE(rels_django.DjangoEnum):
    multiple_text = rels.Column()
    male_text = rels.Column()
    female_text = rels.Column()
    utg_name_form = rels.Column()
    linguistics_restrictions = rels.Column()
    energy_regeneration = rels.Column(related_name='base_race')

    records = (('HUMAN', 0, 'человек', 'люди', 'мужчина', 'женщина',
                technical_words.RACE_HUMANS, _race_linguistics_restrictions('HUMAN'), heroes_relations.ENERGY_REGENERATION.PRAY),
               ('ELF', 1, 'эльф', 'эльфы', 'эльф', 'эльфийка',
                technical_words.RACE_ELFS, _race_linguistics_restrictions('ELF'), heroes_relations.ENERGY_REGENERATION.INCENSE),
               ('ORC', 2, 'орк', 'орки', 'орк', 'оркесса',
                technical_words.RACE_ORCS, _race_linguistics_restrictions('ORC'), heroes_relations.ENERGY_REGENERATION.SACRIFICE),
               ('GOBLIN', 3, 'гоблин', 'гоблины', 'гоблин', 'гоблинша',
                technical_words.RACE_GOBLINS, _race_linguistics_restrictions('GOBLIN'), heroes_relations.ENERGY_REGENERATION.MEDITATION),
               ('DWARF', 4, 'дварф', 'дварфы', 'дварф', 'дварфийка',
                technical_words.RACE_DWARFS, _race_linguistics_restrictions('DWARF'), heroes_relations.ENERGY_REGENERATION.SYMBOLS))


class GAME_STATE(rels_django.DjangoEnum):
    records = (('STOPPED', 0, 'остановлена'),
               ('WORKING', 1, 'запущена'))


class HABIT_INTERVAL(rels_django.DjangoEnum):
    female_text = rels.Column()
    neuter_text = rels.Column()
    place_text = rels.Column()
    left_border = rels.Column()
    right_border = rels.Column()


class HABIT_HONOR_INTERVAL(HABIT_INTERVAL):
    records = (('LEFT_3', 0, 'бесчестный', 'бесчестная', 'бесчестное', 'криминальная столица', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
               ('LEFT_2', 1, 'подлый', 'подлая', 'подлое', 'бандитская вотчина', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
               ('LEFT_1', 2, 'порочный', 'порочная', 'порочное', 'неблагополучный город', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
               ('NEUTRAL', 3, 'себе на уме', 'себе на уме', 'себе на уме', 'обычный город', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
               ('RIGHT_1', 4, 'порядочный', 'порядочная', 'порядочное', 'благополучное поселение', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
               ('RIGHT_2', 5, 'благородный', 'благородная', 'благородное', 'честный город', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
               ('RIGHT_3', 6, 'хозяин своего слова', 'хозяйка своего слова', 'хозяин своего слова', 'оплот благородства', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER))


class HABIT_PEACEFULNESS_INTERVAL(HABIT_INTERVAL):
    records = (('LEFT_3', 0, 'скорый на расправу', 'скорая на расправу', 'скорое на расправу', 'территория вендетт', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
               ('LEFT_2', 1, 'вспыльчивый', 'вспыльчивая', 'вспыльчивое', 'пристанище горячих голов', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
               ('LEFT_1', 2, 'задира', 'задира', 'задира', 'беспокойное место', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
               ('NEUTRAL', 3, 'сдержанный', 'сдержанная', 'сдержаное', 'неприметное поселение', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
               ('RIGHT_1', 4, 'доброхот', 'доброхот', 'доброхот', 'спокойное место', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
               ('RIGHT_2', 5, 'миролюбивый', 'миролюбивая', 'миролюбивое', 'мирное поселение', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
               ('RIGHT_3', 6, 'гуманист', 'гуманист', 'гуманист', 'центр цивилизации', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER))


class HABIT_TYPE(rels_django.DjangoEnum):
    intervals = rels.Column()
    plural_accusative = rels.Column()
    verbose_value = rels.Column()

    records = (('HONOR', 0, 'честь', HABIT_HONOR_INTERVAL, 'чести', 'honor'),
               ('PEACEFULNESS', 1, 'миролюбие', HABIT_PEACEFULNESS_INTERVAL, 'миролюбия', 'peacefulness'))


class ARCHETYPE(rels_django.DjangoEnum):
    power_distribution = rels.Column()
    description = rels.Column()
    allowed_power_types = rels.Column(no_index=True, unique=False)

    records = (('MAGICAL', 0, 'маг', power.PowerDistribution(0.25, 0.75), 'герой предпочитает магию грубой силе', [artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL,
                                                                                                                   artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL,
                                                                                                                   artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL]),
               ('NEUTRAL', 1, 'авантюрист', power.PowerDistribution(0.5, 0.5), 'герой соблюдает баланс между мечом и магией', [artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL,
                                                                                                                               artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                                                                                                                               artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL]),
               ('PHYSICAL', 2, 'воин', power.PowerDistribution(0.75, 0.25), 'герой полагается на воинские умения', [artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                                                                                                                    artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL,
                                                                                                                    artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL]))


class SUPERVISOR_TASK_TYPE(rels_django.DjangoEnum):
    records = (('ARENA_PVP_1X1', 0, 'создать pvp бой на арене'),)


class SUPERVISOR_TASK_STATE(rels_django.DjangoEnum):
    records = (('WAITING', 0, 'ожидает ресурсы'),
               ('PROCESSED', 1, 'обработана'),
               ('ERROR', 2, 'ошибка при обработке'))


class ACTOR(rels_django.DjangoEnum):
    records = (('HERO', 0, 'герой'),
               ('MOB', 1, 'монстр'),
               ('PERSON', 2, 'Мастер'),
               ('COMPANION', 3, 'спутник'))


class COINS_AMOUNT(rels_django.DjangoEnum):
    minumum = rels.Column()

    records = (('NO_MONEY', 0, 'нет денег', 0),
               ('COPPER_1', 1, 'больше 1 монет (1 медяка)', 1),
               ('COPPER_10', 2, 'больше 10 монет (10 медяков)', 10),
               ('SILVER_1', 3, 'больше 100 монет (1 серебряного)', 100),
               ('SILVER_10', 4, 'больше 1000 монет (10 серебряных)', 1000),
               ('GOLD_1', 5, 'больше 10000 монет (1 золотого)', 10000),
               ('GOLD_10', 6, 'больше 100000 монет (10 золотых)', 100000),
               ('GOLD_100', 7, 'больше 1000000 монет (100 золотых)', 1000000),
               ('GOLD_1000', 8, 'больше 10000000 монет (1000 золотых)', 10000000))
