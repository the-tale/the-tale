# -*- coding: utf-8 -*-
import math

from dext.views import handler

from common.utils.decorators import staff_required
from common.utils.resources import Resource

from game.map.roads.storage import waymarks_storage

from game.balance import constants as c, formulas as f

class BalanceResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(BalanceResource, self).__init__(request, *args, **kwargs)

    @staff_required()
    @handler('', method='get')
    def show_balance(self): # pylint: disable=R0914
        tmp_time = [u'начало', u'8 часов', u'день', u'неделя', u'месяц', u'3 месяца', u'6 месяцев', u'1 год', u'2 года', u'3 года']
        tmp_times = [0, 8, 24, 24*7, 24*30, 24*30*3, 24*30*6, 24*30*12, 24*30*12*2, 24*30*12*3]
        tmp_lvls = map(f.lvl_after_time, tmp_times)

        # Всё, что ниже, должно зависеть от уровня, не от времени, т.к. время в данном случае не точный параметр, а анализ всё равно ориентируется на уровень.

        exp_for_quest = f.experience_for_quest__real(waymarks_storage.average_path_length)

        tmp_exp_to_level = map(math.floor, map(f.exp_on_lvl, tmp_lvls))
        tmp_exp_total = map(math.floor, map(f.total_exp_to_lvl, tmp_lvls))

        tmp_quests_to_level = map(math.ceil, map(lambda exp: exp/float(exp_for_quest), tmp_exp_to_level))
        tmp_quests_total = map(math.ceil, map(lambda exp: exp/float(exp_for_quest), tmp_exp_total))

        tmp_hp = map(f.hp_on_lvl, tmp_lvls)
        tmp_turns = map(f.turns_on_lvl, tmp_lvls)
        tmp_turns_to_time = map(int, map(f.hours_to_turns, tmp_times))
        tmp_expected_damage_to_hero_per_hit = map(f.expected_damage_to_hero_per_hit, tmp_lvls)
        tmp_expected_damage_to_hero_per_hit_interval = [ (int(round(dmg*(1-c.DAMAGE_DELTA))), int(round(dmg*(1+c.DAMAGE_DELTA)))) for dmg in tmp_expected_damage_to_hero_per_hit]
        tmp_mob_hp = map(f.mob_hp_to_lvl, tmp_lvls)
        tmp_power = map(f.power_to_lvl, tmp_lvls)
        tmp_expected_damage_to_mob_per_hit = map(f.expected_damage_to_mob_per_hit, tmp_lvls)
        tmp_real_damage_to_mob_per_hit = map(f.damage_from_power, tmp_power)
        tmp_real_damage_to_mob_per_hit_interval = [ (int(round(dmg*(1-c.DAMAGE_DELTA))), int(round(dmg*(1+c.DAMAGE_DELTA)))) for dmg in tmp_real_damage_to_mob_per_hit]
        tmp_power_per_slot = [f.power_to_artifact(x) for x in tmp_lvls]
        tmp_battles_at_lvl = map(math.floor, [x * c.BATTLES_PER_HOUR for x in map(f.time_on_lvl, tmp_lvls)])
        tmp_total_battles = map(math.floor, [x * c.BATTLES_PER_HOUR for x in map(f.total_time_for_lvl, tmp_lvls)])
        tmp_artifacts_per_battle = map(f.artifacts_per_battle, tmp_lvls)
        tmp_artifacts_total = [(lvl-1)*c.ARTIFACTS_PER_LVL for lvl in tmp_lvls]
        tmp_artifacts_per_hour = [x*c.BATTLES_PER_HOUR for x in map(f.artifacts_per_battle, tmp_lvls)]
        tmp_artifacts_per_day = [x*c.BATTLES_PER_HOUR*24 for x in map(f.artifacts_per_battle, tmp_lvls)]

        tmp_gold_at_lvl = map(f.expected_gold_at_lvl, tmp_lvls)
        tmp_gold_in_day = map(f.expected_gold_in_day, tmp_lvls)
        tmp_total_gold_at_lvl = map(f.total_gold_at_lvl, tmp_lvls)

        return self.template('balance/balance.html',
                             {'c': c,
                              'f': f ,

                              'exp_for_quest': exp_for_quest,
                              'average_path_length':waymarks_storage.average_path_length,

                              'tmp_time': tmp_time,
                              'tmp_lvls': tmp_lvls,
                              'tmp_exp_to_level': tmp_exp_to_level,
                              'tmp_exp_total': tmp_exp_total,
                              'tmp_quests_to_level': tmp_quests_to_level,
                              'tmp_quests_total': tmp_quests_total,
                              'tmp_hp': tmp_hp,
                              'tmp_turns': tmp_turns,
                              'tmp_turns_to_time': tmp_turns_to_time,
                              'tmp_expected_damage_to_hero_per_hit': tmp_expected_damage_to_hero_per_hit,
                              'tmp_mob_hp': tmp_mob_hp,
                              'tmp_power': tmp_power,
                              'tmp_expected_damage_to_mob_per_hit': tmp_expected_damage_to_mob_per_hit,
                              'tmp_expected_damage_to_hero_per_hit_interval': tmp_expected_damage_to_hero_per_hit_interval,
                              'tmp_real_damage_to_mob_per_hit': tmp_real_damage_to_mob_per_hit,
                              'tmp_real_damage_to_mob_per_hit_interval': tmp_real_damage_to_mob_per_hit_interval,
                              'tmp_power_per_slot': tmp_power_per_slot,
                              'tmp_battles_at_lvl': tmp_battles_at_lvl,
                              'tmp_total_battles': tmp_total_battles,
                              'tmp_artifacts_total': tmp_artifacts_total,
                              'tmp_artifacts_per_battle': tmp_artifacts_per_battle,
                              'tmp_artifacts_per_hour': tmp_artifacts_per_hour,
                              'tmp_artifacts_per_day': tmp_artifacts_per_day,

                              'tmp_gold_at_lvl': tmp_gold_at_lvl,
                              'tmp_gold_in_day': tmp_gold_in_day,
                              'tmp_total_gold_at_lvl': tmp_total_gold_at_lvl
                              } )
