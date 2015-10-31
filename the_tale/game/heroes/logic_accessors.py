# coding: utf-8
import time
import math
import random
import datetime

from django.conf import settings as project_settings

from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
from the_tale.linguistics.storage import restrictions_storage

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f
from the_tale.game.balance import power

from the_tale.game.prototypes import TimePrototype
from the_tale.game import relations as game_relations

from the_tale.game.map import logic as map_logic


from . import relations
from . import conf


class LogicAccessorsMixin(object):
    __slots__ = ('_cached_modifiers',)

    def reset_accessors_cache(self):
        if not hasattr(self, '_cached_modifiers'):
            self._cached_modifiers = {}
        else:
            self._cached_modifiers.clear()

        # sync some parameters
        self.health = min(self.health, self.max_health)

        if self.companion:
            self.companion.on_accessors_cache_changed()


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
        value = self.equipment.modify_attribute(modifier, value)

        if self.companion and not modifier.is_ADDITIONAL_ABILITIES:
            value = self.companion.modify_attribute(modifier, value)

        return value

    def check_attribute(self, modifier):
        return ( self.abilities.check_attribute(modifier) or
                 self.habit_honor.check_attribute(modifier) or
                 self.habit_peacefulness.check_attribute(modifier) or
                 (self.companion and self.companion.check_attribute(modifier)))

    def update_context(self, hero_actor, enemy):
        self.abilities.update_context(hero_actor, enemy)

        for ability in self.additional_abilities:
            ability.update_context(hero_actor, enemy)

        self.habit_honor.update_context(hero_actor, enemy)
        self.habit_peacefulness.update_context(hero_actor, enemy)


    ################################
    # modifiers
    ################################

    def modify_quest_priority(self, quest):

        priority = quest.priority

        if quest.is_HELP_FRIEND:
            priority *= self.attribute_modifier(relations.MODIFIERS.FRIEND_QUEST_PRIORITY)

        if quest.is_INTERFERE_ENEMY:
            priority *= self.attribute_modifier(relations.MODIFIERS.ENEMY_QUEST_PRIORITY)

        if quest.quest_type.is_CHARACTER:
            priority *= self.attribute_modifier(relations.MODIFIERS.CHARACTER_QUEST_PRIORITY)

        return priority

    def modify_move_speed(self, speed):
        dominant_place = self.position.get_dominant_place()

        if dominant_place is not None:
            return speed * dominant_place.transport
        else:
            return speed * self.position.raw_transport()

    ################################
    # checkers
    ################################

    def is_battle_start_needed(self):
        dominant_place = self.position.get_dominant_place()

        if dominant_place is not None:
            battles_per_turn = 1.0 - dominant_place.safety
        else:
            battles_per_turn = c.BATTLES_PER_TURN + c.WHILD_BATTLES_PER_TURN_BONUS

        battles_per_turn = min(c.MAX_BATTLES_PER_TURN, max(0, battles_per_turn + self.battles_per_turn_summand))

        return random.uniform(0, 1) <=  battles_per_turn


    def can_be_healed(self, strict=False):
        if strict:
            return self.is_alive and self.max_health > self.health

        return self.is_alive and (c.ANGEL_HELP_HEAL_IF_LOWER_THEN * self.max_health > self.health)

    @property
    def need_rest_in_settlement(self): return self.health < self.max_health * c.HEALTH_IN_SETTLEMENT_TO_START_HEAL_FRACTION * self.preferences.risk_level.health_percent_to_rest

    @property
    def need_rest_in_move(self): return self.health < self.max_health * c.HEALTH_IN_MOVE_TO_START_HEAL_FRACTION * self.preferences.risk_level.health_percent_to_rest

    @property
    def need_trade_in_town(self):
        return float(self.bag.occupation) / self.max_bag_size > c.BAG_SIZE_TO_SELL_LOOT_FRACTION

    @property
    def need_equipping(self):
        slot, unequipped, equipped = self.get_equip_candidates() # pylint: disable=W0612
        return equipped is not None

    @property
    def need_regenerate_energy(self):
        return TimePrototype.get_current_turn_number() > self.last_energy_regeneration_at_turn + self.preferences.energy_regeneration_type.period


    def can_change_all_powers(self):
        if self.is_banned:
            return False

        return self.is_premium

    def can_change_person_power(self, person):
        if self.is_banned:
            return False

        return self.can_change_place_power(person.place)

    def can_change_place_power(self, place):
        if self.is_banned:
            return False

        if place.depends_from_all_heroes:
            return True

        return self.is_premium

    @property
    def can_participate_in_pvp(self): return not self.is_fast and not self.is_banned

    @property
    def can_repair_building(self):  return self.is_premium and not self.is_banned


    @property
    def is_ui_caching_required(self):
        return (datetime.datetime.now() - self.ui_caching_started_at).total_seconds() < conf.heroes_settings.UI_CACHING_TIME

    @classmethod
    def is_ui_continue_caching_required(self, ui_caching_started_at):
        return ui_caching_started_at + conf.heroes_settings.UI_CACHING_TIME - conf.heroes_settings.UI_CACHING_CONTINUE_TIME < time.time()


    @property
    def is_premium(self):
        return self.premium_state_end_at > datetime.datetime.now()

    @property
    def is_banned(self):
        return self.ban_state_end_at > datetime.datetime.now()

    @property
    def is_active(self):
        return self.active_state_end_at > datetime.datetime.now()

    def can_be_helped(self):
        if (self.last_help_on_turn == TimePrototype.get_current_turn_number() and
            self.helps_in_turn >= conf.heroes_settings.MAX_HELPS_IN_TURN):
            return False

        return True

    def can_get_artifact_for_quest(self):
        return random.uniform(0, 1) < self.attribute_modifier(relations.MODIFIERS.GET_ARTIFACT_FOR_QUEST)

    def can_safe_artifact_integrity(self, artifact):
        probability = self.safe_artifact_integrity_probability
        if self.preferences.favorite_item is not None and self.preferences.favorite_item == artifact.type.equipment_slot:
            probability += c.ARTIFACT_INTEGRITY_SAFE_PROBABILITY_FOR_FAVORITE_ITEM
        return random.uniform(0, 1) < probability

    def can_companion_steal_money(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_STEAL_MONEY)

    def can_companion_steal_item(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_STEAL_ITEM)

    def can_companion_broke_to_spare_parts(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_SPARE_PARTS)

    def can_companion_regenerate(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_REGENERATE)

    def can_companion_eat(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_MONEY_FOR_FOOD)

    def can_companion_drink_artifact(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_DRINK_ARTIFACT)

    def can_companion_do_exorcism(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_EXORCIST)

    def can_companion_eat_corpses(self):
        return self.check_attribute(relations.MODIFIERS.COMPANION_EAT_CORPSES)

    def can_companion_say_wisdom(self): return self.check_attribute(relations.MODIFIERS.COMPANION_SAY_WISDOM)

    def can_companion_exp_per_heal(self): return self.check_attribute(relations.MODIFIERS.COMPANION_EXP_PER_HEAL)

    def companion_heal_disabled(self):
        return self.preferences.companion_dedication.is_EVERY_MAN_FOR_HIMSELF

    def companion_need_heal(self):
        return self.companion and not self.companion_heal_disabled() and self.companion.need_heal

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

    @property
    def can_upgrade_prefered_slot(self):
        return random.uniform(0, 1) < c.ARTIFACT_FROM_PREFERED_SLOT_PROBABILITY

    @property
    def can_regenerate_double_energy(self):
         return random.uniform(0, 1) < self.regenerate_double_energy_probability

    def can_leave_battle_in_fear(self):
        return random.uniform(0, 1) < self.attribute_modifier(relations.MODIFIERS.FEAR)


    ################################
    # attributes
    ################################

    @property
    def actual_bills_number(self):
        from the_tale.game.bills import conf as bills_conf
        time_border = time.time() - bills_conf.bills_settings.BILL_ACTUAL_LIVE_TIME*24*60*60
        return min(len([bill_voted_time
                        for bill_voted_time in self.actual_bills
                        if bill_voted_time > time_border]),
                   conf.heroes_settings.ACTIVE_BILLS_MAXIMUM)

    @property
    def gender_verbose(self): return self.gender.text

    @property
    def power(self): return power.Power.clean_power_for_hero_level(self.level) + self.equipment.get_power()

    @property
    def basic_damage(self):
        damage = self.power.damage() * self.damage_modifier
        return damage.multiply(self.physic_damage_modifier, self.magic_damage_modifier)

    @property
    def race_verbose(self): return self.race.text

    @property
    def health_percents(self): return float(self.health) / self.max_health


    @property
    def birthday(self): return TimePrototype(self.created_at_turn).game_time

    @property
    def age(self):
        return TimePrototype(TimePrototype.get_current_turn_number() - self.created_at_turn).game_time


    def sell_price(self):
        price = 1 + self.attribute_modifier(relations.MODIFIERS.SELL_PRICE)

        if self.position.place and self.position.place.modifier:
            price += self.position.place.modifier.sell_price()

        return price

    def buy_price(self):
        price = 1 + self.attribute_modifier(relations.MODIFIERS.BUY_PRICE)

        if self.position.place and self.position.place.modifier:
            price += self.position.place.modifier.buy_price()

        return price


    def buy_artifact_power_bonus(self):
        if self.position.place and self.position.place.modifier:
            return self.position.place.modifier.buy_artifact_power_bonus()

        return 0

    @property
    def battles_per_turn_summand(self):
        return self.attribute_modifier(relations.MODIFIERS.BATTLES_PER_TURN)

    @property
    def safe_artifact_integrity_probability(self):
        return self.attribute_modifier(relations.MODIFIERS.SAFE_INTEGRITY)

    @property
    def habits_increase_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.HABITS_INCREASE)

    @property
    def habits_decrease_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.HABITS_DECREASE)

    @property
    def rare_artifact_probability_multiplier(self):
        return self.attribute_modifier(relations.MODIFIERS.RARE)

    @property
    def epic_artifact_probability_multiplier(self):
        return self.attribute_modifier(relations.MODIFIERS.EPIC)

    @property
    def clouded_mind(self):
        return self.attribute_modifier(relations.MODIFIERS.CLOUDED_MIND)

    @property
    def leave_battle_in_fear_probability(self):
        return self.attribute_modifier(relations.MODIFIERS.FEAR)

    @property
    def preferences_change_delay(self):
        return self.attribute_modifier(relations.MODIFIERS.PREFERENCES_CHANCE_DELAY)

    @property
    def additional_abilities(self):
        return self.attribute_modifier(relations.MODIFIERS.ADDITIONAL_ABILITIES)

    @property
    def bonus_artifact_power(self):
        return self.attribute_modifier(relations.MODIFIERS.BONUS_ARTIFACT_POWER)

    @property
    def regenerate_double_energy_probability(self):
        return self.attribute_modifier(relations.MODIFIERS.DOUBLE_ENERGY_REGENERATION)

    @property
    def rest_length(self):
        return int(c.HEAL_LENGTH * self.attribute_modifier(relations.MODIFIERS.REST_LENGTH))

    @property
    def resurrect_length(self):
        return int(self.level * c.TURNS_TO_RESURRECT * self.attribute_modifier(relations.MODIFIERS.RESURRECT_LENGTH))

    @property
    def idle_length(self):
        return int(self.level * c.TURNS_TO_IDLE * self.attribute_modifier(relations.MODIFIERS.IDLE_LENGTH))

    @property
    def energy_maximum(self):
        maximum = c.ANGEL_ENERGY_MAX
        if self.is_premium:
            maximum = c.ANGEL_ENERGY_MAX + c.ANGEL_ENERGY_PREMIUM_BONUS
        return maximum + self.attribute_modifier(relations.MODIFIERS.MAX_ENERGY)

    @property
    def spend_amount(self):
        return int(f.normal_action_price(self.level) * self.next_spending.price_fraction)

    @property
    def energy_discount(self):
        return self.attribute_modifier(relations.MODIFIERS.ENERGY_DISCOUNT)

    @property
    def might_pvp_effectiveness_bonus(self): return f.might_pvp_effectiveness_bonus(self.might)

    @property
    def might_crit_chance(self): return min(1, f.might_crit_chance(self.might) + self.attribute_modifier(relations.MODIFIERS.MIGHT_CRIT_CHANCE))

    @property
    def politics_power_might(self): return f.politics_power_might(self.might)

    @property
    def damage_modifier(self): return self.attribute_modifier(relations.MODIFIERS.DAMAGE)

    @property
    def magic_damage_modifier(self): return self.attribute_modifier(relations.MODIFIERS.MAGIC_DAMAGE)

    @property
    def physic_damage_modifier(self): return self.attribute_modifier(relations.MODIFIERS.PHYSIC_DAMAGE)

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
    def experience_to_next_level(self):
        return f.exp_on_lvl(self.level)

    def spending_priorities(self):
        priorities = self.attribute_modifier(relations.MODIFIERS.ITEMS_OF_EXPENDITURE_PRIORITIES)

        priorities[relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION] *= self.preferences.companion_dedication.heal_spending_priority

        return priorities

    def prefered_quest_markers(self):
        markers = self.attribute_modifier(relations.MODIFIERS.QUEST_MARKERS)
        return set(marker for marker, probability in markers.iteritems() if random.uniform(0, 1) < probability)

    def quest_money_reward_multiplier(self):
        return 1 + self.attribute_modifier(relations.MODIFIERS.QUEST_MONEY_REWARD) + self.preferences.risk_level.reward_modifier

    def quest_markers_rewards_bonus(self):
        return self.attribute_modifier(relations.MODIFIERS.QUEST_MARKERS_REWARD_BONUS)

    def loot_probability(self, mob):
        probability = c.GET_LOOT_PROBABILITY * self.attribute_modifier(relations.MODIFIERS.LOOT_PROBABILITY)
        if self.preferences.mob and self.preferences.mob.type == mob.mob_type:
            probability *= c.PREFERED_MOB_LOOT_PROBABILITY_MULTIPLIER
        return probability

    def artifacts_probability(self, mob):
        probability = c.ARTIFACTS_PER_BATTLE * self.attribute_modifier(relations.MODIFIERS.LOOT_PROBABILITY)
        if mob and self.preferences.mob and self.preferences.mob.type == mob.mob_type:
            probability *= c.PREFERED_MOB_LOOT_PROBABILITY_MULTIPLIER
        return probability

    @property
    def companion_damage(self):
        damage = c.COMPANIONS_DAMAGE_PER_WOUND

        bonus_damage_probability = (c.COMPANIONS_BONUS_DAMAGE_PROBABILITY *
                                    self.companion_damage_probability /
                                    (self.companion._damage_from_heal_probability() + self.companion_damage_probability) )

        if random.random() < bonus_damage_probability:
            damage += self.attribute_modifier(relations.MODIFIERS.COMPANION_DAMAGE)

        return damage

    @property
    def companion_damage_probability(self):
        return self.attribute_modifier(relations.MODIFIERS.COMPANION_DAMAGE_PROBABILITY)

    @property
    def companion_block_probability_multiplier(self):
        return self.attribute_modifier(relations.MODIFIERS.COMPANION_BLOCK_PROBABILITY)

    @property
    def companion_money_for_food_multiplier(self):
        return self.attribute_modifier(relations.MODIFIERS.COMPANION_MONEY_FOR_FOOD)

    @property
    def companion_leave_in_place_probability(self):
        return self.attribute_modifier(relations.MODIFIERS.COMPANION_LEAVE_IN_PLACE)

    @property
    def companion_teleport_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_TELEPORTATOR)

    @property
    def companion_fly_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_FLYER)

    @property
    def companion_abilities_levels(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_ABILITIES_LEVELS)

    @property
    def companion_steal_money_modifier(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_STEAL_MONEY_MULTIPLIER)

    @property
    def companion_steal_artifact_probability_multiplier(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_STEAL_ITEM_MULTIPLIER)

    @property
    def companion_say_wisdom_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_SAY_WISDOM_PROBABILITY)

    @property
    def companion_exp_per_heal_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_EXP_PER_HEAL_PROBABILITY)

    @property
    def companion_eat_corpses_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_EAT_CORPSES_PROBABILITY)

    @property
    def companion_regenerate_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_REGENERATE_PROBABILITY)

    @property
    def companion_drink_artifact_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_DRINK_ARTIFACT_PROBABILITY)

    @property
    def companion_do_exorcism_probability(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_EXORCIST_PROBABILITY)

    @property
    def companion_max_health_multiplier(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_MAX_HEALTH)

    @property
    def companion_max_coherence(self): return self.attribute_modifier(relations.MODIFIERS.COMPANION_MAX_COHERENCE)

    @property
    def companion_heal_probability(self):

        if self.companion is None:
            return 0

        return self.attribute_modifier(self.companion.type.companion_heal_modifier)

    @property
    def companion_coherence_speed(self):

        if self.companion is None:
            return 0

        return self.attribute_modifier(self.companion.type.companion_coherence_modifier)

    @property
    def companion_habits_multiplier(self):
        return self.preferences.companion_empathy.habit_multiplier

    def habit_events(self):
        return self.attribute_modifier(relations.MODIFIERS.HONOR_EVENTS)

    @property
    def habit_quest_active_multiplier(self):
        if self.is_premium:
            return c.HABITS_QUEST_ACTIVE_PREMIUM_MULTIPLIER
        return 1.0

    @property
    def real_time_processing(self):
        return self.is_bot or self.is_active or self.is_premium or (not self.actions.is_single)

    def can_process_turn(self, turn_number):

        if self.is_banned and self.actions.number == 1:
            return False

        if self.real_time_processing:
            return True

        # делаем разброс обрабатываемых с задержкой героев в зависимости от их идентификатора
        # чтобы не делать скачкообразной нагрузки раз в c.INACTIVE_HERO_DELAY ходов
        return (turn_number % conf.heroes_settings.INACTIVE_HERO_DELAY) == (self.id % conf.heroes_settings.INACTIVE_HERO_DELAY)

    @property
    def politics_power_level(self):
        return math.log(self.level, 4)

    @property
    def politics_power_bills(self):
        return self.actual_bills_number * conf.heroes_settings.POWER_PER_ACTIVE_BILL

    @property
    def politics_power_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.POWER)

    @property
    def friend_power_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.POWER_TO_FRIEND)

    @property
    def enemy_power_modifier(self):
        return self.attribute_modifier(relations.MODIFIERS.POWER_TO_ENEMY)

    @property
    def place_power_modifier(self):
        return 0

    def politics_power_multiplier(self, friend=False, enemy=False, hometown=False):
        modifier = 1.0

        if friend:
            modifier += self.friend_power_modifier

        if enemy:
            modifier += self.enemy_power_modifier

        if hometown:
            modifier += self.place_power_modifier

        modifier += self.politics_power_modifier
        modifier += self.politics_power_bills
        modifier += self.politics_power_level
        modifier += self.politics_power_might
        modifier += self.preferences.risk_level.power_modifier

        return max(0, modifier)


    def modify_politics_power(self, power, person=None, place=None):

        is_friend = person and self.preferences.friend and person.id == self.preferences.friend.id
        is_enemy = person and self.preferences.enemy and person.id == self.preferences.enemy.id
        is_hometown = place and self.preferences.place and place.id == self.preferences.place.id

        multiplier = self.politics_power_multiplier(friend=is_friend, enemy=is_enemy, hometown=is_hometown)

        positive_bonus = 0.0
        negative_bonus = 0.0

        if is_friend or is_enemy or is_hometown:
            if power > 0:
                positive_bonus = c.HERO_POWER_BONUS
            elif power < 0:
                negative_bonus = c.HERO_POWER_BONUS

        return (int(power * multiplier), positive_bonus * multiplier, negative_bonus * multiplier)

    mob_type = game_relations.BEING_TYPE.CIVILIZED
    intellect_level = game_relations.INTELLECT_LEVEL.NORMAL
    communication_verbal = game_relations.COMMUNICATION_VERBAL.CAN
    communication_gestures = game_relations.COMMUNICATION_GESTURES.CAN

    @property
    def communication_telepathic(self):
        if self.power.physic < self.power.magic:
            return game_relations.COMMUNICATION_GESTURES.CAN
        return game_relations.COMMUNICATION_GESTURES.CAN_NOT


    ##########################
    # linguistics restrictions
    ##########################

    def linguistics_restrictions_constants(self):
        if not hasattr(self, '_cached_modifiers'):
            self._cached_modifiers = {}

        if '#linguistics_restrictions' in self._cached_modifiers:
            return self._cached_modifiers['#linguistics_restrictions']

        restrictions = (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.GENDER, self.gender.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.RACE, self.race.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR, self.habit_honor.interval.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS, self.habit_honor.interval.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARCHETYPE, self.preferences.archetype.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_VERBAL, self.communication_verbal.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_GESTURES, self.communication_gestures.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_TELEPATHIC, self.communication_telepathic.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.INTELLECT_LEVEL, self.intellect_level.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTOR, game_relations.ACTOR.HERO.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.MOB_TYPE, self.mob_type.value).id,)

        self._cached_modifiers['#linguistics_restrictions'] = restrictions

        return restrictions

    def linguistics_restrictions(self):
        constants = self.linguistics_restrictions_constants()

        terrains = map_logic.get_terrain_linguistics_restrictions(self.position.get_terrain())

        return constants + terrains + (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE, self.actions.current_action.ui_type.value).id,)
