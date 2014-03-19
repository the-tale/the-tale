# coding: utf-8

import math
import random

from django.conf import settings as project_settings

from the_tale.game.balance import constants as c, formulas as f

from the_tale.game.heroes import relations
from the_tale.game.heroes.conf import heroes_settings


class LogicAccessorsMixin(object):

    def reset_accessors_cache(self):
        if not hasattr(self, '_cached_modifiers'):
            self._cached_modifiers = {}
        else:
            self._cached_modifiers.clear()

    def attribute_modifier(self, modifier):

        if not hasattr(self, '_cached_modifiers'):
            self._cached_modifiers = {}

        if not project_settings.TESTS_RUNNING and modifier in self._cached_modifiers:
            return self._cached_modifiers[modifier]

        result = self.modify_attribute(modifier, modifier.default())

        self._cached_modifiers[modifier] = result

        return result

    def modify_attribute(self, modifier, value):
        value = self.abilities.modify_attribute(modifier, value)
        value = self.habit_honor.modify_attribute(modifier, value)
        value = self.habit_peacefulness.modify_attribute(modifier, value)
        return value

    def check_attribute(self, modifier):
        return ( self.abilities.check_attribute(modifier) or
                 self.habit_honor.check_attribute(modifier) or
                 self.habit_peacefulness.check_attribute(modifier) )

    def update_context(self, hero_actor, enemy):
        self.abilities.update_context(hero_actor, enemy)
        self.habit_honor.update_context(hero_actor, enemy)
        self.habit_peacefulness.update_context(hero_actor, enemy)

    ################################
    # modifiers
    ################################

    def modify_sell_price(self, price):
        price *= self.attribute_modifier(relations.MODIFIERS.SELL_PRICE)

        if self.position.place and self.position.place.modifier:
            price = self.position.place.modifier.modify_sell_price(price)

        return int(round(price))

    def modify_buy_price(self, price):
        price *= self.attribute_modifier(relations.MODIFIERS.BUY_PRICE)

        if self.position.place and self.position.place.modifier:
            price = self.position.place.modifier.modify_buy_price(price)

        return int(round(price))

    def modify_quest_priority(self, quest):

        priority = quest.priority

        if quest.is_HELP_FRIEND:
            priority *= self.attribute_modifier(relations.MODIFIERS.FRIEND_QUEST_PRIORITY)

        if quest.is_INTERFERE_ENEMY:
            priority *= self.attribute_modifier(relations.MODIFIERS.ENEMY_QUEST_PRIORITY)

        return priority

    ################################
    # checkers
    ################################

    def can_get_artifact_for_quest(self):
        return self.check_attribute(relations.MODIFIERS.GET_ARTIFACT_FOR_QUEST)

    def can_buy_better_artifact(self):
        if self.check_attribute(relations.MODIFIERS.BUY_BETTER_ARTIFACT):
            return True

        if self.position.place and self.position.place.modifier and self.position.place.modifier.can_buy_better_artifact():
            return True

        return False

    def can_kill_before_battle(self):
        return self.check_attribute(relations.MODIFIERS.KILL_BEFORE_BATTLE)

    def can_peacefull_battle(self, mob_type):
        if mob_type.is_CIVILIZED:
            return self.check_attribute(relations.MODIFIERS.PEACEFULL_BATTLE)
        return False

    def can_picked_up_in_road(self):
        return self.check_attribute(relations.MODIFIERS.PICKED_UP_IN_ROAD)

    def can_get_exp_for_kill(self):
        return self.check_attribute(relations.MODIFIERS.EXP_FOR_KILL)

    @property
    def is_short_quest_path_required(self):
        return self.level < c.QUESTS_SHORT_PATH_LEVEL_CAP

    @property
    def is_first_quest_path_required(self):
        return self.statistics.quests_done == 0

    @property
    def bag_is_full(self): return self.bag.occupation >= self.max_bag_size

    ################################
    # attributes
    ################################

    @property
    def energy_maximum(self):
        if self.is_premium:
            return c.ANGEL_ENERGY_MAX + c.ANGEL_ENERGY_PREMIUM_BONUS
        return c.ANGEL_ENERGY_MAX

    @property
    def might_crit_chance(self): return min(1, f.might_crit_chance(self.might) + self.attribute_modifier(relations.MODIFIERS.MIGHT_CRIT_CHANCE))

    @property
    def damage_modifier(self): return self.attribute_modifier(relations.MODIFIERS.DAMAGE)

    @property
    def move_speed(self): return c.HERO_MOVE_SPEED * self.attribute_modifier(relations.MODIFIERS.SPEED)

    @property
    def initiative(self): return self.attribute_modifier(relations.MODIFIERS.INITIATIVE)

    @property
    def max_health(self): return int(f.hp_on_lvl(self.level) * self.attribute_modifier(relations.MODIFIERS.HEALTH))

    @property
    def max_bag_size(self): return c.MAX_BAG_SIZE + self.attribute_modifier(relations.MODIFIERS.MAX_BAG_SIZE)

    @property
    def experience_modifier(self):
        if self.is_banned:
            return 0.0
        elif self.is_premium:
            modifier = c.EXP_FOR_PREMIUM_ACCOUNT
        else:
            modifier = c.EXP_FOR_NORMAL_ACCOUNT

        modifier *= self.preferences.risk_level.experience_modifier

        return modifier * self.attribute_modifier(relations.MODIFIERS.EXPERIENCE)

    @property
    def person_power_modifier(self):
        return max(math.log(self.level, 2), 0.5) * self.attribute_modifier(relations.MODIFIERS.POWER) * self.preferences.risk_level.power_modifier

    @property
    def friend_power_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.POWER_TO_FRIEND)

    @property
    def enemy_power_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.POWER_TO_ENEMY)

    @property
    def reward_modifier(self):
        return self.preferences.risk_level.reward_modifier

    def spending_priorities(self):
        return self.attribute_modifier(relations.MODIFIERS.ITEMS_OF_EXPENDITURE_PRIORITIES)

    def prefered_quest_markers(self):
        markers = self.attribute_modifier(relations.MODIFIERS.QUEST_MARKERS)
        return set(marker for marker, probability in markers.iteritems() if random.uniform(0, 1) < probability)

    def quest_money_reward_multiplier(self):
        return self.attribute_modifier(relations.MODIFIERS.QUEST_MONEY_REWARD)

    def quest_markers_rewards_bonus(self):
        return self.attribute_modifier(relations.MODIFIERS.QUEST_MARKERS_REWARD_BONUS)

    def loot_probability(self):
        return c.GET_LOOT_PROBABILITY * self.attribute_modifier(relations.MODIFIERS.LOOT_PROBABILITY)

    def artifacts_probability(self):
        return f.artifacts_per_battle(self.level) * self.attribute_modifier(relations.MODIFIERS.LOOT_PROBABILITY)

    def habit_events(self):
        return self.attribute_modifier(relations.MODIFIERS.HONOR_EVENTS)

    @property
    def habit_quest_active_multiplier(self):
        if self.is_premium:
            return c.HABITS_QUEST_ACTIVE_PREMIUM_MULTIPLIER
        return 1.0

    def can_process_turn(self, turn_number):

        if self.is_banned and self.actions.number == 1:
            return False

        if self.is_bot or self.is_active or self.is_premium or (not self.actions.is_single):
            return True

        # делаем разброс обрабатываемых с задержкой героев в зависимости от их идентификатора
        # чтобы не делать скачкообразной нагрузки раз в c.INACTIVE_HERO_DELAY ходов
        return (turn_number % heroes_settings.INACTIVE_HERO_DELAY) == (self.id % heroes_settings.INACTIVE_HERO_DELAY)
