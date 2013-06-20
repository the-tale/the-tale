# coding: utf-8
# pylint: disable=C0302
import random

from dext.utils.urls import url

from common.utils.discovering import discover_classes

from game.heroes.logic import create_mob_for_hero
from game.heroes.statistics import MONEY_SOURCE

from game.map.roads.storage import waymarks_storage

from game.actions import battle, contexts

from game.balance import constants as c, formulas as f, enums as e

from game.actions.exceptions import ActionException

from game.quests.logic import create_random_quest_for_hero

from game.prototypes import TimePrototype

from game.heroes.actions import ActionBase


class ActionIdlenessPrototype(ActionBase):

    TYPE = 'IDLENESS'
    TEXTGEN_TYPE = 'action_idleness'
    EXTRA_HELP_CHOICES = set((c.HELP_CHOICES.START_QUEST,))

    class STATE(ActionBase.STATE):
        QUEST = 'QUEST'
        IN_PLACE = 'IN_PLACE'
        WAITING = 'WAITING'
        REGENERATE_ENERGY = 'regenerate_energy'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero=None, bundle_id=None):
        if hero.actions.has_actions:
            return cls( hero=hero,
                        bundle_id=bundle_id,
                        state=cls.STATE.WAITING)
        else:
            return cls(hero=hero,
                       bundle_id=bundle_id,
                       percents=1.0,
                       state=cls.STATE.WAITING)

    def init_quest(self):

        if not self.leader:
            return False

        self.state = self.STATE.WAITING

        self.percents = 1.0
        self.hero.actions.current_action.percents = self.percents

        self.updated = True

        return True

    def process(self):

        if self.state == self.STATE.IN_PLACE:
            self.state = self.STATE.WAITING
            self.percents = 0

        if self.state == self.STATE.QUEST:
            self.percents = 0
            self.state = self.STATE.IN_PLACE
            ActionInPlacePrototype.create(hero=self.hero)

        if self.state == self.STATE.REGENERATE_ENERGY:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.WAITING:

            self.percents += 1.0 / c.TURNS_TO_IDLE

            if self.percents >= 1.0:
                self.state = self.STATE.QUEST
                quest = create_random_quest_for_hero(self.hero)
                ActionQuestPrototype.create(hero=self.hero, quest=quest)
                self.percents = 0

            elif self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
                ActionRegenerateEnergyPrototype.create(hero=self.hero)
                self.state = self.STATE.REGENERATE_ENERGY

            else:
                if random.uniform(0, 1) < 0.2:
                    self.hero.add_message('action_idleness_waiting', hero=self.hero)


class ActionQuestPrototype(ActionBase):

    TYPE = 'QUEST'
    TEXTGEN_TYPE = 'action_quest'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        PROCESSING = 'processing'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, quest):
        return cls(hero=hero,
                   bundle_id=bundle_id,
                   quest_id=quest.id,
                   state=cls.STATE.PROCESSING)

    def process(self):

        if self.state == self.STATE.PROCESSING:
            percents = self.quest.process(self)

            self.percents = percents

            if self.percents >= 1:
                self.percents = 1
                self.state = self.STATE.PROCESSED


class ActionMoveToPrototype(ActionBase):

    TYPE = 'MOVE_TO'
    TEXTGEN_TYPE = 'action_moveto'
    SHORT_DESCRIPTION = u'путешествует'
    EXTRA_HELP_CHOICES = set((c.HELP_CHOICES.TELEPORT,))

    class STATE(ActionBase.STATE):
        CHOOSE_ROAD = 'choose_road'
        MOVING = 'moving'
        IN_CITY = 'in_city'
        BATTLE = 'battle'
        REGENERATE_ENERGY = 'regenerate_energy'
        RESTING = 'resting'
        RESURRECT = 'resurrect'

    @property
    def destination_id(self): return self.place_id

    @property
    def destination(self): return self.place

    ###########################################
    # Object operations
    ###########################################


    @classmethod
    def _create(cls, hero, bundle_id, destination, break_at=None):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        place_id=destination.id,
                        break_at=break_at,
                        state=cls.STATE.CHOOSE_ROAD)
        hero.add_message('action_moveto_start', hero=hero, destination=destination)
        return prototype

    def get_description_arguments(self):
        args = super(ActionMoveToPrototype, self).get_description_arguments()
        args.update({'destination': self.place})
        return args

    def short_teleport(self, distance):

        if self.state != self.STATE.MOVING:
            return False

        self.hero.position.percents += distance / self.hero.position.road.length
        self.percents += distance / self.length

        if self.hero.position.percents >= 1:
            self.percents -= (self.hero.position.percents - 1) * self.hero.position.road.length / self.length
            self.hero.position.percents = 1

        if self.percents >= 1:
            self.percents = 1

        self.hero.actions.current_action.percents = self.percents

        self.updated = True

        return True

    @property
    def current_destination(self): return self.hero.position.road.point_2 if not self.hero.position.invert_direction else self.hero.position.road.point_1

    def process_choose_road__in_place(self):
        if self.hero.position.place_id != self.destination_id:
            waymark = waymarks_storage.look_for_road(point_from=self.hero.position.place_id, point_to=self.destination_id)
            length =  waymark.length
            self.hero.position.set_road(waymark.road, invert=(self.hero.position.place_id != waymark.road.point_1_id))
            self.state = self.STATE.MOVING
        else:
            length = None
            self.percents = 1
            self.state = self.STATE.PROCESSED

        return length

    def process_choose_road__in_road(self):
        waymark = waymarks_storage.look_for_road(point_from=self.hero.position.road.point_1_id, point_to=self.destination_id)
        road_left = waymark.road
        length_left = waymark.length

        waymark = waymarks_storage.look_for_road(point_from=self.hero.position.road.point_2_id, point_to=self.destination_id)
        road_right = waymark.road
        length_right = waymark.length

        if not self.hero.position.invert_direction:
            delta_left = self.hero.position.percents * self.hero.position.road.length
        else:
            delta_left = (1 - self.hero.position.percents) * self.hero.position.road.length
        delta_rigth = self.hero.position.road.length - delta_left

        if road_left is None:
            invert = True
        elif road_right is None:
            invert = False
        else:
            invert = (length_left + delta_left) < (delta_rigth + length_right)

        if invert:
            length = length_left + delta_left
        else:
            length = delta_rigth + length_right

        percents = self.hero.position.percents
        if self.hero.position.invert_direction and not invert:
            percents = 1 - percents
        elif not self.hero.position.invert_direction and invert:
            percents = 1 - percents

        if length < 0.01:
            current_destination = self.current_destination
            self.hero.position.set_place(current_destination)
            ActionInPlacePrototype.create(hero=self.hero)
            self.state = self.STATE.IN_CITY
        else:
            self.hero.position.set_road(self.hero.position.road, invert=invert, percents=percents)
            self.state = self.STATE.MOVING

        return length


    def process_choose_road(self):

        if self.hero.position.place_id:
            length = self.process_choose_road__in_place()
        else:
            length = self.process_choose_road__in_road()

        if self.length is None:
            self.length = length

    def process_moving(self):
        current_destination = self.current_destination

        if self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY

        elif self.hero.position.is_battle_start_needed():
            mob = create_mob_for_hero(self.hero)
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
            self.state = self.STATE.BATTLE

        else:

            if random.uniform(0, 1) < 0.33:
                self.hero.add_message('action_moveto_move',
                                      hero=self.hero,
                                      destination=self.destination,
                                      current_destination=self.current_destination)

            move_speed = self.hero.move_speed

            dominant_place = self.hero.position.get_dominant_place()
            if dominant_place and dominant_place.modifier:
                move_speed = dominant_place.modifier.modify_move_speed(move_speed)

            delta = move_speed / self.hero.position.road.length

            self.hero.position.percents += delta

            real_length = self.length if self.break_at is None else self.length * self.break_at
            self.percents += move_speed / real_length

            if self.hero.position.percents >= 1:
                self.hero.position.percents = 1
                self.hero.position.set_place(current_destination)
                self.state = self.STATE.IN_CITY
                ActionInPlacePrototype.create(hero=self.hero)

            elif self.break_at and self.percents >= 1:
                self.percents = 1
                self.state = self.STATE.PROCESSED

    def process(self):

        if self.state == self.STATE.RESTING:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.RESURRECT:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.REGENERATE_ENERGY:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.IN_CITY:
            self.state = self.STATE.CHOOSE_ROAD

        if self.state == self.STATE.BATTLE:
            if not self.hero.is_alive:
                ActionResurrectPrototype.create(hero=self.hero)
                self.state = self.STATE.RESURRECT
            else:
                if self.hero.need_rest_in_move:
                    ActionRestPrototype.create(hero=self.hero)
                    self.state = self.STATE.RESTING
                elif self.hero.need_regenerate_energy:
                    ActionRegenerateEnergyPrototype.create(hero=self.hero)
                    self.state = self.STATE.REGENERATE_ENERGY
                else:
                    self.state = self.STATE.MOVING

        if self.state == self.STATE.CHOOSE_ROAD:
            self.process_choose_road()

        if self.state == self.STATE.MOVING:
            self.process_moving()


class ActionBattlePvE1x1Prototype(ActionBase):

    TYPE = 'BATTLE_PVE1x1'
    TEXTGEN_TYPE = 'action_battlepve1x1'
    CONTEXT_MANAGER = contexts.BattleContext

    @property
    def EXTRA_HELP_CHOICES(self): # pylint: disable=C0103
        if self.mob.health <= 0:
            return set()
        return set((c.HELP_CHOICES.LIGHTING,))

    class STATE(ActionBase.STATE):
        BATTLE_RUNNING = 'battle_running'

    ###########################################
    # Object operations
    ###########################################

    def get_info_link(self):
        return url('guide:mobs:info', self.mob.record.id)

    @classmethod
    def _create(cls, hero, bundle_id, mob):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         context=cls.CONTEXT_MANAGER(),
                         mob=mob,
                         mob_context=cls.CONTEXT_MANAGER(),
                         state=cls.STATE.BATTLE_RUNNING)
        hero.add_message('action_battlepve1x1_start', hero=hero, mob=mob)
        return prototype

    def get_description_arguments(self):
        args = super(ActionBattlePvE1x1Prototype, self).get_description_arguments()
        args.update({'mob': self.mob})
        return args

    def bit_mob(self, percents):

        if self.state != self.STATE.BATTLE_RUNNING:
            return False

        self.mob.strike_by(percents)

        self.percents = 1.0 - self.mob.health_percents
        self.hero.actions.current_action.percents = self.percents

        self.updated = True

        return True

    def process(self):

        if self.state == self.STATE.BATTLE_RUNNING:

            # make turn only if mob still alive (it can be killed by angel)
            if self.mob.health > 0:
                old_health = self.hero.health
                battle.make_turn(battle.Actor(self.hero, self.context),
                                 battle.Actor(self.mob, self.mob_context ),
                                 self.hero)
                self.hero_health_lost += old_health - self.hero.health
                self.percents = 1.0 - self.mob.health_percents

            if self.hero.health <= 0:
                self.hero.kill()
                self.hero.statistics.change_pve_deaths(1)
                self.hero.add_message('action_battlepve1x1_diary_hero_killed', important=True, hero=self.hero, mob=self.mob)
                self.state = self.STATE.PROCESSED
                self.percents = 1.0


            if self.mob.health <= 0:
                self.mob.kill()
                self.hero.statistics.change_pve_kills(1)
                self.hero.add_message('action_battlepve1x1_mob_killed', hero=self.hero, mob=self.mob)

                loot = self.mob.get_loot()

                if loot is not None:
                    bag_uuid = self.hero.put_loot(loot)

                    if bag_uuid is not None:
                        if loot.is_useless:
                            self.hero.statistics.change_loot_had(1)
                        else:
                            self.hero.statistics.change_artifacts_had(1)
                        self.hero.add_message('action_battlepve1x1_put_loot', hero=self.hero, artifact=loot, mob=self.mob)
                    else:
                        self.hero.add_message('action_battlepve1x1_put_loot_no_space', hero=self.hero, artifact=loot, mob=self.mob)
                else:
                    self.hero.add_message('action_battlepve1x1_no_loot', hero=self.hero, mob=self.mob)

                self.percents = 1.0
                self.state = self.STATE.PROCESSED

            if self.state == self.STATE.PROCESSED:
                self.remove_mob()


class ActionResurrectPrototype(ActionBase):

    TYPE = 'RESURRECT'
    TEXTGEN_TYPE = 'action_resurrect'
    EXTRA_HELP_CHOICES = set((c.HELP_CHOICES.RESURRECT,))

    class STATE(ActionBase.STATE):
        RESURRECT = 'resurrect'

    @classmethod
    def _create(cls, hero, bundle_id):
        return cls( hero=hero,
                    bundle_id=bundle_id,
                    state=cls.STATE.RESURRECT)

    def fast_resurrect(self):
        if self.state != self.STATE.RESURRECT:
            return False

        self.percents = 1.0
        self.hero.actions.current_action.percents = self.percents

        self.updated = True
        return True


    def process(self):

        if self.state == self.STATE.RESURRECT:

            self.percents += 1.0 / c.TURNS_TO_RESURRECT

            if random.uniform(0, 1) < 0.1:
                self.hero.add_message('action_resurrect_resurrecting', hero=self.hero)

            if self.percents >= 1:
                self.percents = 1
                self.hero.resurrect()
                self.state = self.STATE.PROCESSED
                self.hero.add_message('action_resurrect_finish', hero=self.hero)


class ActionInPlacePrototype(ActionBase):

    TYPE = 'IN_PLACE'
    TEXTGEN_TYPE = 'action_inplace'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        SPEND_MONEY = 'spend_money'
        REGENERATE_ENERGY = 'regenerate_energy'
        CHOOSING = 'choosing'
        TRADING = 'trading'
        RESTING = 'resting'
        EQUIPPING = 'equipping'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         state=cls.STATE.SPEND_MONEY)

        if hero.health < hero.max_health and hero.position.place.modifier and hero.position.place.modifier.full_regen_allowed():
            hero.health = hero.max_health
            hero.add_message('action_inplace_instant_heal', hero=hero, place=hero.position.place)

        return prototype

    def get_description_arguments(self):
        args = super(ActionInPlacePrototype, self).get_description_arguments()
        args.update({'place': self.hero.position.place})
        return args

    def process(self):
        return self.process_settlement()

    def try_to_spend_money(self, gold_amount, money_source):
        if gold_amount <= self.hero.money:
            gold_amount = min(self.hero.money, int(gold_amount * (1 + random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA))))
            gold_amount = self.hero.modify_buy_price(gold_amount)
            self.hero.change_money(money_source, -gold_amount)
            self.hero.switch_spending()
            return gold_amount

        return None

    def spend_money__instant_heal(self):
        coins = self.try_to_spend_money(f.instant_heal_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_HEAL)
        if coins is not None:
            self.hero.health = self.hero.max_health
            self.hero.add_message('action_inplace_diary_instant_heal_for_money', important=True, hero=self.hero, coins=coins)

    def spend_money__buying_artifact(self):
        coins = self.try_to_spend_money(f.buy_artifact_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_ARTIFACTS)
        if coins is not None:

            better = self.hero.can_buy_better_artifact()

            artifact, unequipped, sell_price = self.hero.buy_artifact(better=better, with_preferences=False)

            if unequipped is not None:
                self.hero.add_message('action_inplace_diary_buying_artifact_and_change', important=True,
                                      hero=self.hero, artifact=artifact, coins=coins, old_artifact=unequipped, sell_price=sell_price)
            else:
                self.hero.add_message('action_inplace_diary_buying_artifact', important=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__sharpening_artifact(self):
        coins = self.try_to_spend_money(f.sharpening_artifact_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_SHARPENING)
        if coins is not None:
            artifact = self.hero.sharp_artifact()

            self.hero.add_message('action_inplace_diary_sharpening_artifact', important=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__useless(self):
        coins = self.try_to_spend_money(f.useless_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_USELESS)
        if coins is not None:
            self.hero.add_message('action_inplace_diary_spend_useless', important=True, hero=self.hero, coins=coins)

    def spend_money_impact(self):
        coins = self.try_to_spend_money(f.impact_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_IMPACT)
        if coins is not None:

            choices = []

            if self.hero.preferences.friend_id is not None and self.hero.preferences.friend == self.hero.position.place.id:
                choices.append((True, self.hero.preferences.friend))

            if self.hero.preferences.enemy_id is not None and self.hero.preferences.enemy.place.id == self.hero.position.place.id:
                choices.append((False, self.hero.preferences.enemy))

            if not choices:
                choices.append((random.choice([True, False]), random.choice(self.hero.position.place.persons)))

            impact_type, person = random.choice(choices)

            if impact_type:
                person.cmd_change_power(f.person_power_from_random_spend(1, self.hero.level))
                self.hero.add_message('action_inplace_diary_impact_good', important=True, hero=self.hero, coins=coins, person=person)
            else:
                person.cmd_change_power(f.person_power_from_random_spend(-1, self.hero.level))
                self.hero.add_message('action_inplace_diary_impact_bad', important=True, hero=self.hero, coins=coins, person=person)

    def spend_money(self):

        if self.hero.next_spending == e.ITEMS_OF_EXPENDITURE.INSTANT_HEAL:
            self.spend_money__instant_heal()

        elif self.hero.next_spending == e.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT:
            self.spend_money__buying_artifact()

        elif self.hero.next_spending == e.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT:
            self.spend_money__sharpening_artifact()

        elif self.hero.next_spending == e.ITEMS_OF_EXPENDITURE.USELESS:
            self.spend_money__useless()

        elif self.hero.next_spending == e.ITEMS_OF_EXPENDITURE.IMPACT:
            self.spend_money_impact()

        else:
            raise ActionException('wrong hero money spend type: %d' % self.hero.next_spending)


    def process_settlement(self):

        if self.state == self.STATE.SPEND_MONEY:
            self.state = self.STATE.CHOOSING
            self.spend_money()

        if self.state in [self.STATE.RESTING, self.STATE.EQUIPPING, self.STATE.TRADING, self.STATE.REGENERATE_ENERGY]:
            self.state = self.STATE.CHOOSING

        if self.state == self.STATE.CHOOSING:

            if self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
                self.state = self.STATE.REGENERATE_ENERGY
                ActionRegenerateEnergyPrototype.create(hero=self.hero)

            elif self.hero.need_rest_in_settlement:
                self.state = self.STATE.RESTING
                ActionRestPrototype.create(hero=self.hero)

            elif self.hero.need_equipping_in_town:
                self.state = self.STATE.EQUIPPING
                ActionEquippingPrototype.create(hero=self.hero)

            elif self.hero.need_trade_in_town:
                self.state = self.STATE.TRADING
                ActionTradingPrototype.create(hero=self.hero)

            else:
                self.state = self.STATE.PROCESSED


class ActionRestPrototype(ActionBase):

    TYPE = 'REST'
    TEXTGEN_TYPE = 'action_rest'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        RESTING = 'resting'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         state=cls.STATE.RESTING)
        hero.add_message('action_rest_start', hero=hero)
        return prototype

    def on_heal(self):
        self.percents = float(self.hero.health)/self.hero.max_health
        self.hero.actions.current_action.percents = self.percents

    def process(self):

        if self.hero.health >= self.hero.max_health:
            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.RESTING:

            heal_amount = int(round(float(self.hero.max_health) / c.HEAL_LENGTH * (1 + random.uniform(-c.HEAL_STEP_FRACTION, c.HEAL_STEP_FRACTION))))

            heal_amount = self.hero.heal(heal_amount)

            if random.uniform(0, 1) < 0.2:
                self.hero.add_message('action_rest_resring', hero=self.hero, health=heal_amount)

            self.percents = float(self.hero.health)/self.hero.max_health

            if self.hero.health >= self.hero.max_health:
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.hero.health = self.hero.max_health




class ActionEquippingPrototype(ActionBase):

    TYPE = 'EQUIPPING'
    TEXTGEN_TYPE = 'action_equipping'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        EQUIPPING = 'equipping'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        return cls( hero=hero,
                    bundle_id=bundle_id,
                    state=cls.STATE.EQUIPPING)

    def process(self):

        if self.state == self.STATE.EQUIPPING:
            # TODO: calculate real percents
            self.percents = min(self.percents+0.25, 1)

            slot, unequipped, equipped = self.hero.get_equip_canditates()
            self.hero.change_equipment(slot, unequipped, equipped)
            if equipped:
                if unequipped:
                    if equipped.id == unequipped.id:
                        self.hero.add_message('action_equipping_diary_change_equal_items', important=True, hero=self.hero, item=equipped)
                    else:
                        self.hero.add_message('action_equipping_diary_change_item', important=True, hero=self.hero, unequipped=unequipped, equipped=equipped)
                else:
                    self.hero.add_message('action_equipping_diary_equip_item', important=True, hero=self.hero, equipped=equipped)
            else:
                self.state = self.STATE.PROCESSED


class ActionTradingPrototype(ActionBase):

    TYPE = 'TRADING'
    TEXTGEN_TYPE = 'action_trading'
    SHORT_DESCRIPTION = u'торгует'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        TRADING = 'trading'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         percents_barier=hero.bag.occupation[1],
                         state=cls.STATE.TRADING)
        hero.add_message('action_trading_start', hero=hero)
        return prototype

    def process(self):

        if self.state == self.STATE.TRADING:

            for artifact in self.hero.bag.values():
                if not artifact.quest:
                    sell_price = self.hero.sell_artifact(artifact)
                    self.hero.add_message('action_trading_sell_item', hero=self.hero, artifact=artifact, coins=sell_price)
                    break

            quest_items_count, loot_items_count = self.hero.bag.occupation # pylint: disable=W0612

            if loot_items_count:
                self.percents = 1 - float(loot_items_count - 1) / self.percents_barier
            else:
                self.state = self.STATE.PROCESSED
                self.percents = 1


class ActionMoveNearPlacePrototype(ActionBase):

    TYPE = 'MOVE_NEAR_PLACE'
    TEXTGEN_TYPE = 'action_movenearplace'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        MOVING = 'MOVING'
        BATTLE = 'BATTLE'
        REGENERATE_ENERGY = 'REGENERATE_ENERGY'
        RESTING = 'RESTING'
        RESURRECT = 'RESURRECT'
        IN_CITY = 'IN_CITY'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, place, back):

        if back:
            x, y = place.x, place.y
        else:
            x, y = random.choice(place.nearest_cells)

        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         place_id=place.id,
                         destination_x=x,
                         destination_y=y,
                         state=cls.STATE.MOVING,
                         back=back)

        if hero.position.is_walking:
            from_x, from_y = hero.position.coordinates_to
            hero.position.set_coordinates(from_x, from_y, x, y, percents=0)
        else:
            hero.position.set_coordinates(place.x, place.y, x, y, percents=0)

        return prototype

    def get_description_arguments(self):
        args = super(ActionMoveNearPlacePrototype, self).get_description_arguments()
        args.update({'place': self.place})
        return args

    def process_battle(self):
        if not self.hero.is_alive:
            ActionResurrectPrototype.create(hero=self.hero)
            self.state = self.STATE.RESURRECT
        else:
            if self.hero.need_rest_in_move:
                ActionRestPrototype.create(hero=self.hero)
                self.state = self.STATE.RESTING
            elif self.hero.need_regenerate_energy:
                ActionRegenerateEnergyPrototype.create(hero=self.hero)
                self.state = self.STATE.REGENERATE_ENERGY
            else:
                self.state = self.STATE.MOVING

    def process_moving(self):

        if self.hero.need_rest_in_move:
            ActionRestPrototype.create(hero=self.hero)
            self.state = self.STATE.RESTING

        elif self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY

        elif self.hero.position.is_battle_start_needed():
            mob = create_mob_for_hero(self.hero)
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
            self.state = self.STATE.BATTLE

        else:

            if random.uniform(0, 1) < 0.2:
                self.hero.add_message('action_movenearplace_walk', hero=self.hero, place=self.place)

            if self.hero.position.subroad_len() == 0:
                self.hero.position.percents += 0.1
            else:
                delta = self.hero.move_speed / self.hero.position.subroad_len()
                self.hero.position.percents += delta

            self.percents = self.hero.position.percents

            if self.hero.position.percents >= 1:

                to_x, to_y = self.hero.position.coordinates_to

                if self.back and not (self.place.x == to_x and self.place.y == to_y):
                    # if place was moved
                    from_x, from_y = self.hero.position.coordinates_to
                    self.hero.position.set_coordinates(from_x, from_y, self.place.x, self.place.y, percents=0)
                    return

                self.hero.position.percents = 1
                self.percents = 1

                if self.place.x == to_x and self.place.y == to_y:
                    self.hero.position.set_place(self.place)
                    ActionInPlacePrototype.create(hero=self.hero)
                    self.state = self.STATE.IN_CITY

                else:
                    self.state = self.STATE.PROCESSED


    def process(self):

        if self.state == self.STATE.RESTING:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.RESURRECT:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.REGENERATE_ENERGY:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.IN_CITY:
            if self.percents >= 1:
                self.state = self.STATE.PROCESSED
            else:
                self.state = self.STATE.MOVING

        if self.state == self.STATE.BATTLE:
            self.process_battle()

        if self.state == self.STATE.MOVING:
            self.process_moving()


class ActionRegenerateEnergyPrototype(ActionBase):

    TYPE = 'REGENERATE_ENERGY'
    TEXTGEN_TYPE = 'action_regenerate_energy'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        REGENERATE = 'REGENERATE'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         state=cls.STATE.REGENERATE)

        hero.add_message('action_regenerate_energy_start_%s' % cls.regeneration_slug(hero.preferences.energy_regeneration_type), hero=hero)

        return prototype

    @property
    def description_text_name(self):
        return '%s_description_%s' % (self.TEXTGEN_TYPE, self.regeneration_slug(self.regeneration_type))


    @property
    def regeneration_type(self):
        return self.hero.preferences.energy_regeneration_type

    @classmethod
    def regeneration_slug(cls, regeneration_type):
        return { e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY: 'pray',
                 e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE: 'sacrifice',
                 e.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE: 'incense',
                 e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS: 'symbols',
                 e.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION: 'meditation' }[regeneration_type]

    def step_percents(self):
        return 1.0 / c.ANGEL_ENERGY_REGENERATION_STEPS[self.regeneration_type]

    def process(self):

        if self.state == self.STATE.REGENERATE:

            self.percents += self.step_percents()

            if self.percents >= 1:
                energy_delta = self.storage.heroes[self.hero.id].change_energy(f.angel_energy_regeneration_amount(self.regeneration_type))
                self.hero.last_energy_regeneration_at_turn = TimePrototype.get_current_turn_number()

                if energy_delta:
                    self.hero.add_message('action_regenerate_energy_energy_received_%s' % self.regeneration_slug(self.regeneration_type), hero=self.hero, energy=energy_delta)
                else:
                    self.hero.add_message('action_regenerate_energy_no_energy_received_%s' % self.regeneration_slug(self.regeneration_type), hero=self.hero)

                self.state = self.STATE.PROCESSED


class ActionDoNothingPrototype(ActionBase):

    TYPE = 'DO_NOTHING'
    TEXTGEN_TYPE = 'no texgen type'
    SHORT_DESCRIPTION = u'торгует'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionBase.STATE):
        DO_NOTHING = 'DO_NOTHING'

    @property
    def description_text_name(self):
        return '%s_description' % self.textgen_id

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, duration, messages_prefix, messages_probability):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         percents_barier=duration,
                         extra_probability=messages_probability,
                         textgen_id=messages_prefix,
                         state=cls.STATE.DO_NOTHING)
        hero.add_message('%s_start' % messages_prefix, hero=hero)
        return prototype

    def process(self):

        if self.state == self.STATE.DO_NOTHING:

            self.percents += 1.0001 /  self.percents_barier

            if self.extra_probability is not None and random.uniform(0, 1) < self.extra_probability:
                self.hero.add_message('%s_donothing' % self.textgen_id, hero=self.hero)

            if self.percents >= 1.0:
                self.state = self.STATE.PROCESSED


class ActionMetaProxyPrototype(ActionBase):

    TYPE = 'META_PROXY'
    TEXTGEN_TYPE = 'no texgen type'
    SHORT_DESCRIPTION = u'торгует'
    EXTRA_HELP_CHOICES = set()

    @property
    def description_text_name(self):
        return self.meta_action.description_text_name

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, meta_action):
        return cls( hero=hero,
                    bundle_id=bundle_id,
                    meta_action_id=meta_action.id,
                    state=meta_action.state)

    def process(self):

        self.meta_action.process()

        self.state = self.meta_action.state
        self.percents = self.meta_action.percents



ACTION_TYPES = { action_class.TYPE:action_class
                 for action_class in discover_classes(globals().values(), ActionBase) }
