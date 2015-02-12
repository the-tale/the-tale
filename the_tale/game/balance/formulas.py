# coding: utf-8
import math
import random

from the_tale.game.balance import constants as c

# время изменяется в часах, если размерность не указана отдельно
# при всех вычислениях предполагается, что получаемые значения - это либо поталок (которого героя может достигнуть при активной игре пользователя) либо среднее

def turns_to_hours(turns): return float(turns * c.TURN_DELTA) / 60 / 60 # перевод ходов в часы

def turns_to_minutes(turns): return float(turns * c.TURN_DELTA)/60 # перевод ходов в минуты

def hours_to_turns(hours): return float(hours * c.TURNS_IN_HOUR) # перевод часов в ходы

def time_on_lvl(lvl): return float(c.TIME_TO_LVL_DELTA * lvl * c.TIME_TO_LVL_MULTIPLIER ** lvl) # время, которое игрок проведёт на одном уровне

def exp_on_lvl(lvl): return int(c.EXP_PER_HOUR * time_on_lvl(lvl)) # опыт, который игрок должен заработать на одном уровне

def hp_on_lvl(lvl): return int(c.INITIAL_HP + c.HP_PER_LVL * (lvl - 1)) # здоровье игрока, достигшего уровня

def turns_on_lvl(lvl):  return int(hours_to_turns(time_on_lvl(lvl))) # количество ходов, которое герой проведёт на уровне

def total_time_for_lvl(lvl): return float(sum(time_on_lvl(x) for x in xrange(1, lvl))) # общее время, затрачиваемое героем на достижение уровня (с 1-ого)

def total_exp_to_lvl(lvl): return int(sum(exp_on_lvl(x) for x in xrange(1, lvl+1))) # общий опыт, получаемые героем для стижения уровня (с 1-ого)

def lvl_after_time(time):
    total_exp = c.EXP_PER_HOUR * time
    level = 1
    while total_exp > exp_on_lvl(level):
        total_exp -= exp_on_lvl(level)
        level += 1
    return level

def mob_hp_to_lvl(lvl): return int(hp_on_lvl(lvl) * c.MOB_HP_MULTIPLIER) # здоровье моба уровня героя
def boss_hp_to_lvl(lvl): return int(hp_on_lvl(lvl) * c.BOSS_HP_MULTIPLIER) # здоровье босса уровня героя

def expected_damage_to_hero_per_hit(lvl): return float(hp_on_lvl(lvl) * c.DAMAGE_TO_HERO_PER_HIT_FRACTION) # ожидаемый урон моба по герою за удар
def expected_damage_to_mob_per_hit(lvl): return float(mob_hp_to_lvl(lvl) * c.DAMAGE_TO_MOB_PER_HIT_FRACTION) # ожидаемый урон героя по мобу за удар

def battles_on_lvl(lvl): return int(time_on_lvl(lvl) * c.BATTLES_PER_HOUR)

# на текущий момент предполагаем, что из моба всегда может упась артефакт, подходящий герою по уровню
# цена добычи из моба указанного уровня (т.е. для моба, появляющегося на этом уровне)
# таким образом, нет необходимости поддерживать добычу для каждого моба для каждого уровня, достаточно по одному предмету каждого качества,
# а остальное по мере фантазии чисто для разнообразия
def normal_loot_cost_at_lvl(lvl): return  int(math.ceil(c.NORMAL_LOOT_COST * lvl))
def medium_loot_cost_at_lvl(lvl): return sum(normal_loot_cost_at_lvl(i) for i in xrange(1, lvl+1)) / lvl

def sell_artifact_price(lvl): return normal_loot_cost_at_lvl(lvl) * c.SELL_ARTIFACT_PRICE_MULTIPLIER

def expected_normal_gold_at_lvl(lvl):
    MAGIC = 1.0
    QUESTS_IN_DAY = 2.0

    battles = battles_on_lvl(lvl)
    artifact_price = sell_artifact_price(lvl)

    loot_cost = battles * c.GET_LOOT_PROBABILITY * medium_loot_cost_at_lvl(lvl)
    artifacts_cost = battles * c.ARTIFACTS_PER_BATTLE * artifact_price
    quests_cost = QUESTS_IN_DAY * time_on_lvl(lvl) / 24 * artifact_price

    return int((loot_cost + artifacts_cost + quests_cost) * MAGIC)

# при рассчётах принимаем, что герой будет встречать мобов разных уровней с одинаковой вероятностью
def expected_gold_in_day(lvl): return int(math.floor(expected_normal_gold_at_lvl(lvl) / (time_on_lvl(lvl) / 24)))
def total_gold_at_lvl(lvl): return int(sum(expected_normal_gold_at_lvl(x) for x in xrange(1, lvl+1)))

def normal_action_price(lvl):
    return int(expected_gold_in_day(lvl))

def gold_in_path(lvl, path_length):
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


def turns_to_game_time(turns):
    game_time = turns * c.GAME_SECONDS_IN_TURN

    year = int(game_time / c.GAME_SECONDS_IN_GAME_YEAR)
    game_time %= int(c.GAME_SECONDS_IN_GAME_YEAR)

    month = int(game_time / c.GAME_SECONDS_IN_GAME_MONTH) + 1
    game_time %= int(c.GAME_SECONDS_IN_GAME_MONTH)

    day = int(game_time / c.GAME_SECONDS_IN_GAME_DAY) + 1
    game_time %= int(c.GAME_SECONDS_IN_GAME_DAY)

    hour = int(game_time / c.GAME_SECONDS_IN_GAME_HOUR)
    game_time %= int(c.GAME_SECONDS_IN_GAME_HOUR)

    minute = int(game_time / c.GAME_SECONDS_IN_GAME_MINUTE)
    game_time %= int(c.GAME_SECONDS_IN_GAME_MINUTE)

    second = game_time

    return (year, month, day, hour, minute, second)

# величина конкретного типа регенерации энергии
def angel_energy_regeneration_amount(regeneration_type):
    return c.ANGEL_ENERGY_REGENERATION_DELAY[regeneration_type] * c.ANGEL_ENERGY_REGENERATION_AMAUNT

# периодичность конкретного типа регенерации энергии (в ходах)
def angel_energy_regeneration_delay(regeneration_type):
    return c.ANGEL_ENERGY_REGENERATION_DELAY[regeneration_type] * c.ANGEL_ENERGY_REGENERATION_PERIOD


# могущество
def might_crit_chance(might):
    if might < 1:
        return 0
    return math.log(might, 10) / 10.0

def might_pvp_effectiveness_bonus(might):
    if might < 1:
        return 0
    return math.log(might, 10) / 40.0


def path_to_turns(path_length):
    return path_length / c.DISTANCE_IN_ACTION_CYCLE * c.ACTIONS_CYCLE_LENGTH

def experience_for_quest__real(max_path_length):
    MAGIC_QUEST_MULTIPLIER = 0.7
    return path_to_turns(max_path_length) / c.TURNS_IN_HOUR * c.EXP_PER_HOUR * MAGIC_QUEST_MULTIPLIER

def experience_for_quest(max_path_length):
    return  int(math.ceil(experience_for_quest__real(max_path_length) * random.uniform(1.0-c.EXP_PER_QUEST_FRACTION, 1+c.EXP_PER_QUEST_FRACTION)))

#########################################
# расчёт изменения влияния песроанажа
#########################################

def person_power_from_random_spend(power_points, hero_lvl):
    return power_points * math.log(hero_lvl, 2) * c.PERSON_POWER_FOR_RANDOM_SPEND

def person_power_for_quest__real(path_length):
    # multiply by 2 since in most quests hero must return to start point
    return 2 * path_to_turns(path_length) / c.TURNS_IN_HOUR * (c.HERO_POWER_PER_DAY / 24.0)

def person_power_for_quest(path_length):
    return  int(math.ceil(person_power_for_quest__real(path_length) * random.uniform(1.0-c.PERSON_POWER_PER_QUEST_FRACTION, 1+c.PERSON_POWER_PER_QUEST_FRACTION)))

def max_ability_points_number(level):
    maximum = 1 * 1 + (c.ABILITIES_BATTLE_MAXIMUM - 1) * 5 + c.ABILITIES_NONBATTLE_MAXIMUM * 5 + c.ABILITIES_COMPANION_MAXIMUM * 5
    return min(level + 2, maximum)

# города
def place_goods_production(level):
    return level * c.PLACE_GOODS_BONUS

def place_goods_consumption(level):
    return level * c.PLACE_GOODS_BONUS

def companions_coherence_for_level(level):
    # если меняется, необходимо пересчитать количество опыта за квест для спутника
    return level

def companions_defend_in_battle_probability(coherence):
    # вероятность того, что удар противника в бою встретит спутник
    coherence_multiplier = 1 + (float(coherence) / c.COMPANIONS_MAX_COHERENCE - 0.5) / 0.5 * c.COMPANIONS_BLOCK_MULTIPLIER_COHERENCE_DELTA
    return coherence_multiplier * float(c.COMPANIONS_DEFENDS_IN_BATTLE) / (c.BATTLE_LENGTH / 2)


def companions_heal_in_hour(current_health, max_health):
    health_fraction = float(current_health) / max_health
    return c.COMPANIONS_HEAL_MIN_IN_HOUR + (c.COMPANIONS_HEAL_MAX_IN_HOUR - c.COMPANIONS_HEAL_MIN_IN_HOUR) * health_fraction


def companions_heal_length(current_health, max_health):
    # длительность действия ухода за спутнкиком считается с разбросом в 0.25 от среднего
    heal_multiplier = 1 + (0.5 - float(current_health) / max_health) / 0.5 * 0.25
    heal_length = float(c.COMPANIONS_HEAL_FRACTION * c.TURNS_IN_HOUR) * heal_multiplier
    heal_in_hour = companions_heal_in_hour(current_health, max_health)
    return int(math.ceil(heal_length / heal_in_hour))
