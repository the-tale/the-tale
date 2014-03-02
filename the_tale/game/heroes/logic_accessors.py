# coding: utf-8

import math

from the_tale.game.balance import constants as c, formulas as f

from the_tale.game.heroes import relations


class LogicAccessorsMixin(object):

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
        price = self.modify_attribute(relations.MODIFIERS.SELL_PRICE, price)

        if self.position.place and self.position.place.modifier:
            price = self.position.place.modifier.modify_sell_price(price)

        return int(round(price))

    def modify_buy_price(self, price):
        price = self.modify_attribute(relations.MODIFIERS.BUY_PRICE, price)

        if self.position.place and self.position.place.modifier:
            price = self.position.place.modifier.modify_buy_price(price)

        return int(round(price))

    def modify_quest_priority(self, quest):

        priority = quest.priority

        if quest.is_HELP_FRIEND:
            priority = self.modify_attribute(relations.MODIFIERS.FRIEND_QUEST_PRIORITY, priority)

        if quest.is_INTERFERE_ENEMY:
            priority = self.modify_attribute(relations.MODIFIERS.ENEMY_QUEST_PRIORITY, priority)

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
    def might_crit_chance(self): return self.modify_attribute(relations.MODIFIERS.MIGHT_CRIT_CHANCE, f.might_crit_chance(self.might))

    @property
    def damage_modifier(self): return self.modify_attribute(relations.MODIFIERS.DAMAGE, 1)

    @property
    def move_speed(self): return self.modify_attribute(relations.MODIFIERS.SPEED, c.HERO_MOVE_SPEED)

    @property
    def initiative(self): return self.modify_attribute(relations.MODIFIERS.INITIATIVE, 1)

    @property
    def max_health(self): return int(f.hp_on_lvl(self.level) * self.modify_attribute(relations.MODIFIERS.HEALTH, 1))

    @property
    def max_bag_size(self): return self.modify_attribute(relations.MODIFIERS.MAX_BAG_SIZE, c.MAX_BAG_SIZE)

    @property
    def experience_modifier(self):
        if self.is_banned:
            modifier = 0.0
        elif self.is_premium:
            modifier = c.EXP_FOR_PREMIUM_ACCOUNT
        elif self.is_active:
            modifier = c.EXP_FOR_NORMAL_ACCOUNT
        else:
            modifier = c.EXP_FOR_NORMAL_ACCOUNT * c.EXP_PENALTY_MULTIPLIER

        modifier *= self.preferences.risk_level.experience_modifier

        return self.modify_attribute(relations.MODIFIERS.EXPERIENCE, modifier)

    @property
    def person_power_modifier(self):
        return self.modify_attribute(relations.MODIFIERS.POWER, max(math.log(self.level, 2), 0.5)) * self.preferences.risk_level.power_modifier

    @property
    def friend_power_modifier(self):
        return self.modify_attribute(relations.MODIFIERS.POWER_TO_FRIEND, 1.0)

    @property
    def enemy_power_modifier(self):
        return self.modify_attribute(relations.MODIFIERS.POWER_TO_ENEMY, 1.0)

    @property
    def reward_modifier(self):
        return self.preferences.risk_level.reward_modifier

    def spending_priorities(self):
        priorities = {record:record.priority for record in relations.ITEMS_OF_EXPENDITURE.records}
        return self.modify_attribute(relations.MODIFIERS.ITEMS_OF_EXPENDITURE_PRIORITIES, priorities)

    def prefered_quest_markers(self):
        return self.modify_attribute(relations.MODIFIERS.QUEST_MARKERS, set())

    def quest_markers_rewards_bonus(self):
        return self.modify_attribute(relations.MODIFIERS.QUEST_MARKERS_REWARD_BONUS, {})

    def loot_probability(self):
        return self.modify_attribute(relations.MODIFIERS.LOOT_PROBABILITY, c.GET_LOOT_PROBABILITY)

    def artifacts_probability(self):
        return self.modify_attribute(relations.MODIFIERS.LOOT_PROBABILITY, f.artifacts_per_battle(self.level))

    def habit_events(self):
        return self.modify_attribute(relations.MODIFIERS.HONOR_EVENTS, set())

    @property
    def habit_quest_active_multiplier(self):
        if self.is_premium:
            return c.HABITS_QUEST_ACTIVE_PREMIUM_MULTIPLIER
        return 1.0
