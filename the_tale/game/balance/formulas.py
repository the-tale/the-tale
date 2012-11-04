# coding: utf-8
import math
import random

from . import constants as c

# время изменяется в часах, если размерность не указана отдельно
# при всех вычислениях предполагается, что получаемые значения - это либо поталок (которого героя может достигнуть при активной игре пользователя) либо среднее

def turns_to_hours(turns): return float(turns * c.TURN_DELTA) / 60 / 60 # перевод ходов в часы

def turns_to_minutes(turns): return float(turns * c.TURN_DELTA)/60 # перевод ходов в минуты

def hours_to_turns(hours): return float(hours * c.TURNS_IN_HOUR) # перевод часов в ходы

def time_on_lvl(lvl): return float(c.TIME_TO_LVL_DELTA * lvl) # время, которое игрок проведёт на одном уровне

def exp_on_lvl(lvl): return int(c.EXP_PER_HOUR * time_on_lvl(lvl)) # опыт, который игрок должен заработать на одном уровне

def hp_on_lvl(lvl): return int(c.INITIAL_HP + c.HP_PER_LVL * (lvl - 1)) # здоровье игрока, достигшего уровня

def turns_on_lvl(lvl):  return int(hours_to_turns(time_on_lvl(lvl))) # количество ходов, которое герой проведёт на уровне

def total_time_for_lvl(lvl): return float(sum(time_on_lvl(x) for x in xrange(1, lvl))) # общее время, затрачиваемое героем на достижение уровня (с 1-ого)

def total_exp_to_lvl(lvl): return int(sum(exp_on_lvl(x) for x in xrange(1, lvl+1))) # общий опыт, получаемые героем для стижения уровня (с 1-ого)

# находим зависимость уровня от проведённого времени

# уровень героя, после проведения в игре time времени
# решаем уравнение: Solve[time == totalTimeForLvl[lvl], lvl];
# и добавляем 1
def lvl_after_time(time): return int(1 + (-c.TIME_TO_LVL_DELTA + math.sqrt(c.TIME_TO_LVL_DELTA) * math.sqrt(8 * time + c.TIME_TO_LVL_DELTA)) / (2 * c.TIME_TO_LVL_DELTA))

# чистая сила героя на уровень
def clean_power_to_lvl(lvl): return int(lvl * c.POWER_PER_LVL)

# общая ожидаемая сила артефактов, надетых на героя указанного уровня к моменту получения следующего уровня
# рассматривался альтернативный вариант - зависимость силы, от времени, но в этом случае она растёт очень быстро, что плохо сказывается на цифрах урона и т.п.
def power_to_lvl(lvl): return int(lvl * c.POWER_TO_LVL)

def power_to_artifact(lvl): return power_to_lvl(lvl) / c.EQUIP_SLOTS_NUMBER

# функция, для получения случайного значения силы артефакта
def power_to_artifact_interval(lvl):
    base_power = power_to_artifact(lvl)
    delta = int(base_power * c.ARTIFACT_POWER_DELTA)
    min_power = max(base_power - delta, 1)
    max_power = base_power + delta
    return min_power, max_power

def power_to_artifact_randomized(lvl):
    return random.randint(*power_to_artifact_interval(lvl))


# Предполагаем, что мобы различаются по инициативе (скорости), здоровью и урону. Каждый из этих параметров высчитывается как процент от среднего (ожидаемого) значения.
# Таким образом, каждый параметр может быть, например от 0.5 до 1.5. Сложность моба расчитывается по формуле, учитывающей влияние этих параметров на задержку героя
# в сравнении с битвой со средним мобом. Опыт даётся пропорционально сложности.
#

def mob_hp_to_lvl(lvl): return int(hp_on_lvl(lvl) * c.MOB_HP_MULTIPLIER) # здоровье моба уровня героя

def expected_damage_to_hero_per_hit(lvl): return float(hp_on_lvl(lvl) * c.DAMAGE_TO_HERO_PER_HIT_FRACTION) # ожидаемый урон моба по герою за удар
def expected_damage_to_mob_per_hit(lvl): return float(mob_hp_to_lvl(lvl) * c.DAMAGE_TO_MOB_PER_HIT_FRACTION) # ожидаемый урон героя по мобу за удар

# находим зависимость урона, наносимого героем от его силы
# для этого опираясь на силу, оцениваем уровень героя, на котором она может быть и исходя из этого делаем предположение об уроне мобу
# т.к. здоровье моба зависит от здоровья героя, то полученая формула должна быть применима и в PvP - т.е. бои просто будут идти дольше
# решаем уравнение:  Solve[power == powerToLvl[lvl], lvl];
# ВНИМАНИЕ: должен быть float
def expected_lvl_from_power(power): return float(power) / (c.POWER_PER_LVL + c.POWER_TO_LVL) # оцениваемый уровень героя, исходя из его силы

def damage_from_power(power): return float(expected_damage_to_mob_per_hit(expected_lvl_from_power(power)))  # урон, наносимый героем


# сложность моба рассчитывается как влияние оказываемое им на скорость протекания боёв и на длительность цепочки боёв (в боях, т.е. как быстро здоровье снимает)
# формула:
# сложность = урон *              // влияет только на длительность цепочки
#             здоровье ** 2 *     // влияет и на длительность цепочки и на длительность боя
#             скорость *          // влияет на длительность цепочки (т.е. снимет здоровье в speed раз больше)
#             (1+скорость) / 2    // влияет на длительность боя
#
def mob_difficulty(speed, health, damage): return damage * health**2 * speed * (1+speed) / 2

def battles_on_lvl(lvl): return int(time_on_lvl(lvl) * c.BATTLES_PER_HOUR)

# вероятность выпаденя артефакта из моба (т.е. вероятноть получить артефакт после боя)
def artifacts_per_battle(lvl): return float(c.ARTIFACTS_PER_LVL) / battles_on_lvl(lvl)

# на текущий момент предполагаем, что из моба всегда может упась артефакт, подходящий герою по уровню
# в то же время очевидно, что будет давольно странно на протяжении всей игры получать один и тот же артефакт существенно разной силы из мобов, которых бил ещё на 1-ом уровне
# следовательно, необходимо ограничивать артефакты уровнем, т.е. организовывать в список, как мобов и добычу (см. далее)
# следовательно, необходимо поддерживать список артефактов для каждого моба таким, что бы для героя любого уровня находилась добыча
# обеспечивать подобное требования сложновато, но, теоретически, можно
# возможно, получится ввести широкие уровневые границы для получения артефактов, т.к. они получаются героем достаточно редко.
# ВОПРОС: что должно быть разнообразней: экипировка (артефакты) или добыча? предположительно артефакты

# цена добычи из моба указанного уровня (т.е. для моба, появляющегося на этом уровне)
# таким образом, нет необходимости поддерживать добычу для каждого моба для каждого уровня, достаточно по одному предмету каждого качества,
# а остальное по мере фантазии чисто для разнообразия
def normal_loot_cost_at_lvl(lvl): return  int(math.ceil(c.NORMAL_LOOT_COST * lvl))
def rare_loot_cost_at_lvl(lvl): return int(math.ceil(c.RARE_LOOT_COST * lvl))
def epic_loot_cost_at_lvl(lvl): return int(math.ceil(c.EPIC_LOOT_COST * lvl))
def expected_normal_gold_at_lvl(lvl): return int(math.floor(battles_on_lvl(lvl) * c.GET_LOOT_PROBABILITY * (c.NORMAL_LOOT_PROBABILITY * normal_loot_cost_at_lvl(lvl) +
                                                                                                            c.RARE_LOOT_PROBABILITY * rare_loot_cost_at_lvl(lvl) +
                                                                                                            c.EPIC_LOOT_PROBABILITY * epic_loot_cost_at_lvl(lvl))))

# при рассчётах принимаем, что герой будет встречать мобов разных уровней с одинаковой вероятностью
def expected_gold_at_lvl(lvl): return int(math.floor(sum(expected_normal_gold_at_lvl(x) for x in xrange(1, lvl+1)) / lvl))
def expected_gold_in_day(lvl): return int(math.floor(expected_gold_at_lvl(lvl) / (time_on_lvl(lvl) / 24)))
def total_gold_at_lvl(lvl): return int(sum(expected_gold_at_lvl(x) for x in xrange(1, lvl)))

# в общем случае, за уровень герой должен тратить процентов на 10 меньше золота, чем зарабатывать
# тратить деньги можно на следующие вещи:
# - моментальное лечение
# - покупка нового артефакта
# - "заточка" экипированного артефакта
# - безполезные траты
# - изменение (+/-) влияния персонажей
#
# предполагаем, что трата денег должна происходит примерно раз в какое-то время
# следовательно, исходя из скорости накопления денег, можно посчиать среднюю цену одной операции
# конкретные цены каждого типа операций могут варьироваться так, что бы их среднее было приближено к средней цене
# так как возможность произвести трату денег есть далеко не каждый ход, то нужно знать частоты посещения городов и прочих ключевых точек
# альтернатива - сделать псевдослучайную последовательность, которая управляет тем, какое действие будет совершено в следующий раз
# при этом на него копятся деньги, а по накоплении оно может возникнуть с какой-то большой вероятностью (что бы срабатывать достаточно быстро, не не сиюминуту)
# выбираем второй вараинт, как более управляемый

def normal_action_price(lvl): return int(expected_gold_in_day(lvl) * c.NORMAL_ACTION_PRICE_MULTIPLYER)
def instant_heal_price(lvl): return int(normal_action_price(lvl) * c.INSTANT_HEAL_PRICE_FRACTION)
def buy_artifact_price(lvl): return int(normal_action_price(lvl) * c.BUY_ARTIFACT_PRICE_FRACTION)
def sharpening_artifact_price(lvl): return int(normal_action_price(lvl) * c.SHARPENING_ARTIFACT_PRICE_FRACTION)
def useless_price(lvl): return int(normal_action_price(lvl) * c.USELESS_PRICE_FRACTION)
def impact_price(lvl): return int(normal_action_price(lvl) * c.IMPACT_PRICE_FRACTION)

# +1 top power - to prevent total zero power -> zero lvl
# +1 to slots - to emulate heroe's clean power
def sell_artifact_price(lvl):
    # lvl = int(math.ceil(expected_lvl_from_power((power+1)*c.EQUIP_SLOTS_NUMBER)))
    return int(buy_artifact_price(lvl) * c.SELL_ARTIFACT_PRICE_FRACTION)

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
# - по выполнении квеста, каждому персонажу начисляется влияние равное +/- (<уровень героя>*<константа>)
#   -  учитывается влияние на проятжении месяца
#   -  общее влияние равно сумме влияний за месяц с коофициентом давности, т.е. влияние, полученное месяц назад, применяется с коофициентом 0 (не влияет)

#########################################
# расчёт изменения влияния песроанажа
#########################################

def person_power_from_quest(power_points, hero_lvl, quest_length): # длительность задания указывается в ходах
    # do not give any power for heroes on first level
    return int(power_points * math.log(hero_lvl, 2) * c.HERO_POWER_PER_DAY * (quest_length / (24 * c.TURNS_IN_HOUR)))

def person_power_from_random_spend(power_points, hero_lvl):
    return power_points * math.log(hero_lvl, 2) * c.PERSON_POWER_FOR_RANDOM_SPEND


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
