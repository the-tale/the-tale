
import smart_imports

smart_imports.all()


class GENDER(rels_django.DjangoEnum):
    utg_id = rels.Column(no_index=False)
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
    religion_type = rels.Column(related_name='base_race')

    records = (('HUMAN', 0, 'человек', 'люди', 'мужчина', 'женщина',
                technical_words.RACE_HUMANS, _race_linguistics_restrictions('HUMAN'), heroes_relations.RELIGION_TYPE.PRAY),
               ('ELF', 1, 'эльф', 'эльфы', 'эльф', 'эльфийка',
                technical_words.RACE_ELFS, _race_linguistics_restrictions('ELF'), heroes_relations.RELIGION_TYPE.INCENSE),
               ('ORC', 2, 'орк', 'орки', 'орк', 'оркесса',
                technical_words.RACE_ORCS, _race_linguistics_restrictions('ORC'), heroes_relations.RELIGION_TYPE.SACRIFICE),
               ('GOBLIN', 3, 'гоблин', 'гоблины', 'гоблин', 'гоблинша',
                technical_words.RACE_GOBLINS, _race_linguistics_restrictions('GOBLIN'), heroes_relations.RELIGION_TYPE.MEDITATION),
               ('DWARF', 4, 'дварф', 'дварфы', 'дварф', 'дварфийка',
                technical_words.RACE_DWARFS, _race_linguistics_restrictions('DWARF'), heroes_relations.RELIGION_TYPE.SYMBOLS))


class GAME_STATE(rels_django.DjangoEnum):
    records = (('STOPPED', 0, 'остановлена'),
               ('WORKING', 1, 'запущена'))


class HABIT_INTERVAL(rels_django.DjangoEnum):
    female_text = rels.Column()
    neuter_text = rels.Column()
    place_text = rels.Column()
    left_border = rels.Column()
    right_border = rels.Column()
    direction = rels.Column(unique=False)


class HABIT_HONOR_INTERVAL(HABIT_INTERVAL):
    records = (('LEFT_3', 0, 'бесчестный', 'бесчестная', 'бесчестное', 'криминальная столица', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0], -1),
               ('LEFT_2', 1, 'подлый', 'подлая', 'подлое', 'бандитская вотчина', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1], -1),
               ('LEFT_1', 2, 'порочный', 'порочная', 'порочное', 'неблагополучный город', c.HABITS_RIGHT_BORDERS[1],  c.HABITS_RIGHT_BORDERS[2], -1),
               ('NEUTRAL', 3, 'себе на уме', 'себе на уме', 'себе на уме', 'обычный город', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3], 0),
               ('RIGHT_1', 4, 'порядочный', 'порядочная', 'порядочное', 'благополучное поселение', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4], 1),
               ('RIGHT_2', 5, 'благородный', 'благородная', 'благородное', 'честный город', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5], 1),
               ('RIGHT_3', 6, 'хозяин своего слова', 'хозяйка своего слова', 'хозяин своего слова', 'оплот благородства', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER, 1))


class HABIT_PEACEFULNESS_INTERVAL(HABIT_INTERVAL):
    records = (('LEFT_3', 0, 'скорый на расправу', 'скорая на расправу', 'скорое на расправу', 'территория вендетт', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0], -1),
               ('LEFT_2', 1, 'вспыльчивый', 'вспыльчивая', 'вспыльчивое', 'пристанище горячих голов', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1], -1),
               ('LEFT_1', 2, 'задира', 'задира', 'задира', 'беспокойное место', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2], -1),
               ('NEUTRAL', 3, 'сдержанный', 'сдержанная', 'сдержаное', 'неприметное поселение', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3], 0),
               ('RIGHT_1', 4, 'доброхот', 'доброхот', 'доброхот', 'спокойное место', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4], 1),
               ('RIGHT_2', 5, 'миролюбивый', 'миролюбивая', 'миролюбивое', 'мирное поселение', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5], 1),
               ('RIGHT_3', 6, 'гуманист', 'гуманист', 'гуманист', 'центр цивилизации', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER, 1))


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

    records = (('MAGICAL', 0, 'маг', power.PowerDistribution(0.25, 0.75), 'герой предпочитает магию грубой силе',
                [artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL,
                 artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL,
                 artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL]),
               ('NEUTRAL', 1, 'авантюрист', power.PowerDistribution(0.5, 0.5), 'герой соблюдает баланс между мечом и магией',
                [artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL,
                 artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                 artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL]),
               ('PHYSICAL', 2, 'воин', power.PowerDistribution(0.75, 0.25), 'герой полагается на воинские умения',
                [artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL,
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
               ('COMPANION', 3, 'спутник'),
               ('EMISSARY', 4, 'эмиссар'))


class COINS_AMOUNT(rels_django.DjangoEnum):
    minumum = rels.Column(unique=False)
    maximum = rels.Column(unique=False)

    MAXIMUM = 10**20

    records = (('NO_MONEY', 0, 'нет денег', 0, 1),

               ('MIN_COPPER_1', 1, 'больше 1 монет (1 медяка)', 1, MAXIMUM),
               ('MIN_COPPER_10', 2, 'больше 10 монет (10 медяков)', 10, MAXIMUM),
               ('MIN_SILVER_1', 3, 'больше 100 монет (1 серебряного)', 100, MAXIMUM),
               ('MIN_SILVER_10', 4, 'больше 1000 монет (10 серебряных)', 1000, MAXIMUM),
               ('MIN_GOLD_1', 5, 'больше 10000 монет (1 золотого)', 10000, MAXIMUM),
               ('MIN_GOLD_10', 6, 'больше 100000 монет (10 золотых)', 100000, MAXIMUM),
               ('MIN_GOLD_100', 7, 'больше 1000000 монет (100 золотых)', 1000000, MAXIMUM),
               ('MIN_GOLD_1000', 8, 'больше 10000000 монет (1000 золотых)', 10000000, MAXIMUM),

               ('MAX_COPPER_10', 9, 'меньше 10 монет (10 медяков)', 0, 10),
               ('MAX_SILVER_1', 10, 'меньше 100 монет (1 серебряного)', 0, 100),
               ('MAX_SILVER_10', 11, 'меньше 1000 монет (10 серебряных)', 0, 1000),
               ('MAX_GOLD_1', 12, 'меньше 10000 монет (1 золотого)', 0, 10000),
               ('MAX_GOLD_10', 13, 'меньше 100000 монет (10 золотых)', 0, 100000),
               ('MAX_GOLD_100', 14, 'меньше 1000000 монет (100 золотых)', 0, 1000000),
               ('MAX_GOLD_1000', 15, 'меньше 10000000 монет (1000 золотых)', 0, 10000000),

               ('BETWEEN_0_10', 16, '0 <= монет < 10 ', 0, 10),
               ('BETWEEN_10_100', 17, '10 <= монет < 100', 10, 100),
               ('BETWEEN_100_1000', 18, '100 <= монет < 1000', 100, 1000),
               ('BETWEEN_1000_10000', 19, '1000 <= монет < 10000', 1000, 10000),
               ('BETWEEN_10000_100000', 20, '10000 <= монет < 100000', 10000, 100000),
               ('BETWEEN_100000_1000000', 21, '100000 <= монет < 1000000', 100000, 1000000))
