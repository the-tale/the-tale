
import smart_imports

smart_imports.all()

# время изменяется в часах, если размерность не указана отдельно
# при всех вычислениях предполагается, что получаемые значения - это либо поталок (которого героя может достигнуть при активной игре пользователя) либо среднее


def turns_to_hours(turns: float) -> float:
    return turns * c.TURN_DELTA / 60 / 60  # перевод ходов в часы


def turns_to_minutes(turns: float) -> float:
    return turns * c.TURN_DELTA / 60  # перевод ходов в минуты


def hours_to_turns(hours: float) -> float:
    return hours * c.TURNS_IN_HOUR  # перевод часов в ходы


def time_on_lvl(lvl: int) -> float:
    return c.TIME_TO_LVL_DELTA * lvl * c.TIME_TO_LVL_MULTIPLIER ** lvl  # время, которое игрок проведёт на одном уровне


def exp_on_lvl(lvl: int) -> int:
    return int(c.EXP_PER_HOUR * time_on_lvl(lvl))  # опыт, который игрок должен заработать на одном уровне


def hp_on_lvl(lvl: float) -> int:
    return int(c.INITIAL_HP + c.HP_PER_LVL * (lvl - 1))  # здоровье игрока, достигшего уровня


def turns_on_lvl(lvl: int) -> int:
    return int(hours_to_turns(time_on_lvl(lvl)))  # количество ходов, которое герой проведёт на уровне


def total_time_for_lvl(lvl: int) -> float:
    return sum(time_on_lvl(x) for x in range(1, lvl))  # общее время, затрачиваемое героем на достижение уровня (с 1-ого)


def total_exp_to_lvl(lvl: int) -> int:
    return sum(exp_on_lvl(x) for x in range(1, lvl + 1))  # общий опыт, получаемые героем для стижения уровня (с 1-ого)


def lvl_after_time(time: float) -> int:
    total_exp = c.EXP_PER_HOUR * time
    level = 1
    while total_exp > exp_on_lvl(level):
        total_exp -= exp_on_lvl(level)
        level += 1
    return level


def mob_hp_to_lvl(lvl: float) -> int:
    return int(hp_on_lvl(lvl) * c.MOB_HP_MULTIPLIER)  # здоровье моба уровня героя


def boss_hp_to_lvl(lvl: int) -> int:
    return int(hp_on_lvl(lvl) * c.BOSS_HP_MULTIPLIER)  # здоровье босса уровня героя


def expected_damage_to_hero_per_hit(lvl: int) -> float:
    return hp_on_lvl(lvl) * c.DAMAGE_TO_HERO_PER_HIT_FRACTION  # ожидаемый урон моба по герою за удар


def expected_damage_to_mob_per_hit(lvl: float) -> float:
    return mob_hp_to_lvl(lvl) * c.DAMAGE_TO_MOB_PER_HIT_FRACTION  # ожидаемый урон героя по мобу за удар


# на текущий момент предполагаем, что из моба всегда может упась артефакт, подходящий герою по уровню
# цена добычи из моба указанного уровня (т.е. для моба, появляющегося на этом уровне)
# таким образом, нет необходимости поддерживать добычу для каждого моба для каждого уровня, достаточно по одному предмету каждого качества,
# а остальное по мере фантазии чисто для разнообразия

def normal_loot_cost_at_lvl(lvl: int) -> int:
    return int(c.NORMAL_LOOT_COST * math.log(lvl, 1.3)) + 1


def medium_loot_cost_at_lvl(lvl: int) -> int:
    return sum(normal_loot_cost_at_lvl(i) for i in range(1, lvl + 1)) // lvl

# при рассчётах принимаем, что герой будет встречать мобов разных уровней с одинаковой вероятностью


def expected_gold_in_day(lvl: int) -> int:
    loot_cost = c.BATTLES_PER_HOUR * 24 * c.GET_LOOT_PROBABILITY * medium_loot_cost_at_lvl(lvl)
    return int(1 + loot_cost // c.INCOME_LOOT_FRACTION)


def artifacts_in_day() -> float:
    return c.ARTIFACTS_LOOT_PER_DAY + c.EXPECTED_QUESTS_IN_DAY


def sell_artifact_price(lvl: int) -> int:
    return 1 + int((expected_gold_in_day(lvl) * c.INCOME_ARTIFACTS_FRACTION) / artifacts_in_day())


def total_gold_at_lvl(lvl: int) -> int:
    top_level = int(math.floor(lvl))
    before_level = int(sum(expected_gold_in_day(x) * time_on_lvl(x) / 24 for x in range(1, top_level)))
    on_level = (expected_gold_in_day(top_level + 1) * time_on_lvl(top_level + 1) // 24) * (lvl - top_level)
    return int(before_level + on_level)


def normal_action_price(lvl: int) -> int:
    return int(expected_gold_in_day(lvl))


def gold_in_path(lvl: int, path_length: float) -> int:
    return int(expected_gold_in_day(lvl) * path_to_turns(path_length) / float(24 * c.TURNS_IN_HOUR))

# в общем случае, за уровень герой должен тратить процентов на 10 меньше золота, чем зарабатывать
# тратить деньги можно на следующие вещи:
# - моментальное лечение
# - покупка нового артефакта
# - "заточка" экипированного артефакта
# - безполезные траты
# - изменение (+/-) влияния жителей
#
# предполагаем, что трата денег должна происходит примерно раз в какое-то время
# следовательно, исходя из скорости накопления денег, можно посчиать среднюю цену одной операции
# конкретные цены каждого типа операций могут варьироваться так, что бы их среднее было приближено к средней цене
# так как возможность произвести трату денег есть далеко не каждый ход, то нужно знать частоты посещения городов и прочих ключевых точек
# альтернатива - сделать псевдослучайную последовательность, которая управляет тем, какое действие будет совершено в следующий раз
# при этом на него копятся деньги, а по накоплении оно может возникнуть с какой-то большой вероятностью (что бы срабатывать достаточно быстро, не не сиюминуту)
# выбираем второй вараинт, как более управляемый


# задания (квесты)
#  - игрок всегда должен получать полезную/интересную награду за выполнение задания
#  - сложность заданий (точнее количество этапов в них) должно расти с уровнем
#  - со сложностью задания должна увеличиваться вероятность получения эпичной награды (вместо просто "крутой")
#  - возможные награды:
#  - артефакт (даются редко, так что можно позвволить себе давать их и за квесты)
# - особо редкая и дорогая добыча
# - звания, клички, прозвища
#    - лоре-вещи (книги, легенды, карты сокровищ)
#    - элементы кастомизации образа (совсем на будущее, когда появится портрет героя)

# распределение влияния в городах и прочих местах
# требования:
# - с ростом уровня героя, влияние игрока должно расти
#   - с ростом сложности задачи влияние игрока должно расти
#   - влияние, полученное от конкретного задания должно пропадать через некоторое время
#   - у каждого акта влияния должна быть достаточная длительность для:
#   - предотвращения внезапных изменений карты, вызванных случайными скачками
#     - создания эффекта памяти
#     - оставления возможности влиять не ситуацию флеш-мобами
#  получаем:
# - по выполнении квеста, каждому жителю начисляется влияние равное +/- (<уровень героя>*<константа>)
#   -  учитывается влияние на проятжении месяца
#   -  общее влияние равно сумме влияний за месяц с коофициентом давности, т.е. влияние, полученное месяц назад, применяется с коофициентом 0 (не влияет)


# могущество
def might_crit_chance(might: float) -> float:
    if might < 1:
        return 0
    return math.log(might, 10) / 10.0


def politics_power_might(might: float) -> float:
    if might < 1:
        return 0
    return math.log(might, 10) / 10.0


def politics_power_for_level(level: int) -> float:
    return math.log(level, 4)


def normal_job_power(heroes_number: int) -> float:
    magic = 3  # магическое число, отражающее сложность выполнения проекта
    return c.HERO_POWER_PER_DAY * c.NORMAL_JOB_LENGTH * c.EXPECTED_HERO_QUEST_POWER_MODIFIER * heroes_number * magic


def might_pvp_effectiveness_bonus(might: float) -> float:
    if might < 1:
        return 0
    return math.log(might, 10) / 40.0


def path_to_turns(path_length: float) -> float:
    return path_length / c.DISTANCE_IN_ACTION_CYCLE * c.ACTIONS_CYCLE_LENGTH


def experience_for_quest__real(max_path_length: float) -> float:
    MAGIC_QUEST_MULTIPLIER = 0.7
    return path_to_turns(max_path_length) / c.TURNS_IN_HOUR * c.EXP_PER_HOUR * MAGIC_QUEST_MULTIPLIER


def experience_for_quest(max_path_length: float) -> float:
    return int(math.ceil(experience_for_quest__real(max_path_length) * random.uniform(1.0 - c.EXP_PER_QUEST_FRACTION,
                                                                                      1.0 + c.EXP_PER_QUEST_FRACTION)))

#########################################
# расчёт изменения влияния песроанажа
#########################################


def person_power_for_quest__real(path_length: float) -> float:
    # multiply by 2 since in most quests hero must return to start point
    return 2 * path_to_turns(path_length) / c.TURNS_IN_HOUR * (c.HERO_POWER_PER_DAY / 24.0)


def person_power_for_quest(path_length: float) -> int:
    return int(math.ceil(person_power_for_quest__real(path_length) * random.uniform(1.0 - c.PERSON_POWER_PER_QUEST_FRACTION,
                                                                                    1.0 + c.PERSON_POWER_PER_QUEST_FRACTION)))


def max_ability_points_number(level: int) -> int:
    maximum = 1 * 1 + (c.ABILITIES_BATTLE_MAXIMUM - 1) * 5 + c.ABILITIES_NONBATTLE_MAXIMUM * 5 + c.ABILITIES_COMPANION_MAXIMUM * 5
    return min(level + 2, maximum)


# города

def place_specialization_modifier(size: int) -> float:
    return (math.log(size, 2) + 1) / 1.7


def person_max_specialization_points() -> float:
    # два идеальных мастера с влиянием по 30% должны давать PLACE_TYPE_NECESSARY_BORDER влияния в городе 10-ого уровня
    # points * 2 * max_spec * 0.3 * place_specialization_modifier(10) = PLACE_TYPE_NECESSARY_BORDER
    # points = PLACE_TYPE_NECESSARY_BORDER / (2 * max_spec * 0.3 * place_specialization_modifier(10))
    MAX_SPEC = 3
    return c.PLACE_TYPE_NECESSARY_BORDER / (2 * MAX_SPEC * 0.3 * place_specialization_modifier(10))


def place_specialization_from_person(person_points: float, politic_power_fraction: float, place_size_multiplier: float) -> float:
    return person_max_specialization_points() * person_points * politic_power_fraction * place_size_multiplier


def companions_coherence_for_level(level: int) -> int:
    # если меняется, необходимо пересчитать количество опыта за квест для спутника
    return level


def companions_defend_in_battle_probability(coherence: float) -> float:
    # вероятность того, что удар противника в бою встретит спутник
    coherence_multiplier = 1 + (float(coherence) / c.COMPANIONS_MAX_COHERENCE - 0.5) / 0.5 * c.COMPANIONS_BLOCK_MULTIPLIER_COHERENCE_DELTA
    return coherence_multiplier * c.COMPANIONS_DEFEND_PROBABILITY


def companions_heal_length(current_health: int, max_health: int) -> int:
    # длительность действия ухода за спутнкиком считается с разбросом в 0.5 от среднего
    heal_multiplier = 1 + (0.5 - float(current_health) / max_health) / 0.5 * 0.5
    heal_length = float(c.COMPANIONS_HEAL_FRACTION * c.TURNS_IN_HOUR) * heal_multiplier
    return int(math.ceil(heal_length / c.COMPANIONS_HEALS_IN_HOUR))
