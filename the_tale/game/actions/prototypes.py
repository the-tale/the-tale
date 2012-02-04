# -*- coding: utf-8 -*-
import random

from dext.utils.decorators import nested_commit_on_success
from dext.utils import s11n

from ..heroes.logic import create_mob_for_hero, heal_in_town, sell_in_city, equip_in_city
from ..heroes.conf import heroes_settings
from ..heroes.habilities import ABILITIES_EVENTS as HERO_ABILITIES_EVENTS
from ..heroes.prototypes import EXPERIENCE_VALUES
from ..heroes.hmessages import generator as msg_generator

from ..map.places.prototypes import get_place_by_model
from ..map.roads.prototypes import get_road_by_model, WaymarkPrototype

from .models import Action, UNINITIALIZED_STATE

def get_actions_types():
    actions = {}
    for key, cls in globals().items():
        if isinstance(cls, type) and issubclass(cls, ActionPrototype) and cls != ActionPrototype:
            actions[cls.TYPE] = cls
    return actions

def get_action_by_model(model):
    if model is None: 
        return None

    return ACTION_TYPES[model.type](model=model)


class ActionException(Exception): pass

class ActionPrototype(object):
    
    TYPE = 'BASE'
    SHORT_DESCRIPTION = 'undefined'
    ENTROPY_BARRIER = 100

    class STATE:
        UNINITIALIZED = UNINITIALIZED_STATE
        PROCESSED = 'processed'

    def __init__(self, model, *argv, **kwargs):
        super(ActionPrototype, self).__init__(*argv, **kwargs)
        self.model = model
        self.removed = False
        self.bundle = None

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type

    @property
    def order(self): return self.model.order

    def set_bundle(self, bundle):
        self.bundle = bundle

    def get_leader(self): return self.model.leader
    def set_leader(self, value): self.model.leader = value
    leader = property(get_leader, set_leader)

    def get_percents(self): return self.model.percents
    def set_percents(self, value): self.model.percents = value
    percents = property(get_percents, set_percents)

    def get_state(self): return self.model.state
    def set_state(self, value): self.model.state = value
    state = property(get_state, set_state)

    def get_entropy(self): return self.model.entropy
    def set_entropy(self, value): self.model.entropy = value
    entropy = property(get_entropy, set_entropy)

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def hero(self):
        return self.bundle.heroes[self.hero_id]

    @property
    def parent(self):
        return self.bundle.actions[self.model.parent_id]

    @property
    def road_id(self): return self.model.road_id

    @property
    def place_id(self): return self.model.place_id

    @property
    def place(self):
        if not hasattr(self, '_place'):
            self._place = get_place_by_model(model=self.model.place)
        return self._place

    def get_road(self):
        if not hasattr(self, '_road'):
            self._road = get_road_by_model(model=self.model.road)
        return self._road
    def set_road(self, value):
        if hasattr(self, '_road'):
            delattr(self, '_road')
        self.model.road = value.model
    road = property(get_road, set_road)

    @property
    def mob(self):
        from ..mobs.prototypes import get_mob_by_data
        if not hasattr(self, '_mob'):
            data = s11n.from_json(self.model.mob)
            if not data:
                self._mob = None
            else:
                self._mob = get_mob_by_data(data=data)
        return self._mob

    def remove_mob(self):
        delattr(self, '_mob')
        self.model.mob = '{}'

    @property
    def quest(self):
        from ..quests.prototypes import get_quest_by_model
        if not hasattr(self, '_quest'):
            self._quest = get_quest_by_model(model=self.model.quest)
        return self._quest

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def break_at(self): return self.model.break_at

    def get_length(self): return self.model.length
    def set_length(self, value): self.model.length = value
    length = property(get_length, set_length)

    def get_destination(self): return self.model.destination_x, self.model.destination_y
    def set_destination(self, x, y):
        self.model.destination_x = x
        self.model.destination_y = y

    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        self.bundle.remove_action(self)
        if hasattr(self, '_quest'):
            self.quest.remove()
        self.model.delete()
        self.removed = True

    def save(self): 
        if hasattr(self, '_data'):
            self.model.data = s11n.to_json(self._data)
        if hasattr(self, '_mob'):
            self.model.mob = s11n.to_json(self._mob.serialize())
        if hasattr(self, '_quest'):
            self._quest.save()
        self.model.save(force_update=True)

    def on_die(self):
        self.remove()
        return False

    def ui_info(self):
        return {'id': self.id,
                'type': self.type,
                'short_description': self.SHORT_DESCRIPTION,
                'percents': self.percents,
                'entropy': self.entropy,
                'entropy_barier': self.ENTROPY_BARRIER,
                'specific': {'place_id': self.place_id,
                             'road_id': self.road_id,
                             'mob': self.mob.ui_info() if self.mob else None},
                'data': self.data #TODO: get json directly from self.model.data, without reloading it
                }

    def process_action(self):

        self.process()

        if not self.removed:

            if self.state == self.STATE.PROCESSED:
                self.parent.leader = True
                # self.parent.save()
                self.remove()
            else:
                # self.save()
                pass

    def process_turn(self, turn_number):
        self.process_action()
        return turn_number + 1


class ActionIdlenessPrototype(ActionPrototype):

    TYPE = 'IDLENESS'
    SHORT_DESCRIPTION = u'бездельничает'
    ENTROPY_BARRIER = 100

    class STATE(ActionPrototype.STATE):
        WAITING = 'waiting'
        ACTING = 'acting'

    ###########################################
    # Object operations
    ###########################################

    def on_die(self):
        self.bundle.add_action(ActionResurrectPrototype.create(self))
        return True

    @classmethod
    @nested_commit_on_success
    def create(cls, parent=None, hero=None):
        if parent:
            parent.leader = False
            model = Action.objects.create( type=cls.TYPE, parent=parent.model, hero=parent.hero.model, order=parent.order+1)
        else:
            model = Action.objects.create( type=cls.TYPE, hero=hero.model, order=0)
        return cls(model=model)

    def init_quest(self):

        if self.state != self.STATE.WAITING:
            return False

        self.entropy = self.ENTROPY_BARRIER
        self.percents = 1.0

        return True

    def process(self):

        if self.state in [self.STATE.UNINITIALIZED, self.STATE.ACTING]:
            self.entropy = 0
            self.percents = 0
            self.state = self.STATE.WAITING

        elif self.state == self.STATE.WAITING:

            self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)
            self.percents = float(self.entropy) / self.ENTROPY_BARRIER

            if random.uniform(0, 1) < 0.2:
                self.hero.push_message(msg_generator.msg_action_idleness_waiting(self.hero))

            if (self.entropy >= self.ENTROPY_BARRIER / 2 and 
                (self.hero.need_trade_in_town or self.hero.need_rest_in_town) and 
                self.hero.position.is_settlement):

                self.bundle.add_action(ActionInPlacePrototype.create(self, self.hero.position.place))

                self.state = self.STATE.ACTING

            elif self.entropy >= self.ENTROPY_BARRIER:
                from ..quests.logic import create_random_quest_for_hero

                self.entropy = 0

                self.hero.push_message(msg_generator.msg_action_idleness_start_quest(self.hero))
                quest = create_random_quest_for_hero(self.hero)

                self.bundle.add_action(ActionQuestPrototype.create(parent=self, quest=quest))

                self.state = self.STATE.ACTING


class ActionQuestPrototype(ActionPrototype):

    TYPE = 'QUEST'
    SHORT_DESCRIPTION = u'выполняет задание'

    class STATE(ActionPrototype.STATE):
        PROCESSING = 'processing'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, quest):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model, 
                                       hero=parent.hero.model, 
                                       order=parent.order+1, 
                                       quest=quest.model)
        return cls(model=model)

    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.PROCESSING
        
        elif self.state == self.STATE.PROCESSING:
            finish, percents = self.quest.process(self)

            self.percents = percents

            if finish:
                self.state = self.STATE.PROCESSED
                # self.quest.remove()
            else:
                # self.quest.save()
                pass

            # self.hero.save()


class ActionMoveToPrototype(ActionPrototype):

    TYPE = 'MOVE_TO'
    SHORT_DESCRIPTION = u'путешествует'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        CHOOSE_ROAD = 'choose_road'
        MOVING = 'moving'
        IN_CITY = 'walking_in_city'
        BATTLE = 'battle'

    destination_id = ActionPrototype.place_id
    destination = ActionPrototype.place

    ###########################################
    # Object operations
    ###########################################


    @classmethod
    @nested_commit_on_success
    def create(cls, parent, destination, break_at=None):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model, 
                                       order=parent.order+1, 
                                       place=destination.model,
                                       break_at=break_at)
        return cls(model=model)

    def short_teleport(self, distance):

        if self.state != self.STATE.MOVING:
            return False

        self.hero.position.percents += distance / self.road.length
        self.percents += distance / self.length

        if self.hero.position.percents >= 1:
            self.percents -= (self.hero.position.percents - 1) * self.road.length / self.length
            self.hero.position.percents = 1

        if self.percents >= 1:
            self.percents = 1

        return True

    @property
    def current_destination(self): return self.road.point_2 if not self.hero.position.invert_direction else self.road.point_1

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.hero.push_message(msg_generator.msg_action_moveto_start(self.hero, self.destination))
            self.percents = 0
            self.state = self.STATE.CHOOSE_ROAD

        elif self.state == self.STATE.CHOOSE_ROAD:
            # print 'CHOOSE_ROAD start'
            # print self.destination.name

            if self.hero.position.place_id:
                # print 'in place'
                if self.hero.position.place_id != self.destination_id:
                    self.road, length = WaymarkPrototype.look_for_road(point_from=self.hero.position.place_id, point_to=self.destination_id)
                    self.hero.position.set_road(self.road, invert=(self.hero.position.place_id != self.road.point_1_id))
                    self.state = self.STATE.MOVING
                else:
                    length = None
                    self.percents = 1
                    self.state = self.STATE.PROCESSED
            else:
                # print ('on road ', 
                #        self.hero.position.road.point_1.name, self.hero.position.road.point_2.name, 
                #        self.hero.position.invert_direction, self.hero.position.percents )
                road_left, length_left = WaymarkPrototype.look_for_road(point_from=self.hero.position.road.point_1_id, point_to=self.destination_id)
                road_right, length_right = WaymarkPrototype.look_for_road(point_from=self.hero.position.road.point_2_id, point_to=self.destination_id)

                # print road_left, length_left
                # print road_right, length_right

                if not self.hero.position.invert_direction:
                    delta_left = self.hero.position.percents * self.hero.position.road.length
                else:
                    delta_left = (1 - self.hero.position.percents) * self.hero.position.road.length
                delta_rigth = self.hero.position.road.length - delta_left
                
                # print delta_left, delta_rigth

                if road_left is None:
                    invert = True
                elif road_right is None:
                    invert = False
                else:
                    invert = (length_left + delta_left) < (delta_rigth + length_right)

                # print invert

                if invert:
                    length = length_left + delta_left
                else:
                    length = delta_rigth + length_right

                # print length

                percents = self.hero.position.percents
                if self.hero.position.invert_direction and not invert:
                    percents = 1 - percents
                elif not self.hero.position.invert_direction and invert:
                    percents = 1 - percents

                # print percents

                if length < 0.01:
                    current_destination = self.current_destination
                    self.hero.position.set_place(current_destination)
                    self.state = self.STATE.IN_CITY
                else:
                    self.road = self.hero.position.road
                    self.hero.position.set_road(self.hero.position.road, invert=invert, percents=percents)
                    # print ('new road ', 
                    #        self.hero.position.road.point_1.name, self.hero.position.road.point_2.name, 
                    #        self.hero.position.invert_direction, self.hero.position.percents )
                    self.state = self.STATE.MOVING

            if self.length is None:
                self.length = length

        elif self.state == self.STATE.MOVING:

            current_destination = self.current_destination

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
                mob = create_mob_for_hero(self.hero)

                self.bundle.add_action(ActionBattlePvE_1x1Prototype.create(parent=self, mob=mob))

                self.state = self.STATE.BATTLE
            else:
                self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)

                if random.uniform(0, 1) < 0.33:
                    self.hero.push_message(msg_generator.msg_action_moveto_move(self.hero, self.destination, self.current_destination))
            
                delta = self.hero.move_speed / self.road.length

                self.hero.position.percents += delta

                real_length = self.length if self.break_at is None else self.length * self.break_at
                self.percents += self.hero.move_speed / real_length

                if self.hero.position.percents >= 1:
                    self.hero.position.percents = 1
                    self.hero.position.set_place(current_destination)
                    
                    self.state = self.STATE.IN_CITY

                    self.bundle.add_action(ActionInPlacePrototype.create(parent=self, settlement=current_destination))

                elif self.break_at and self.percents >= 1:
                    self.percents = 1
                    self.state = self.STATE.PROCESSED                    

        elif self.state == self.STATE.BATTLE:
            self.state = self.STATE.MOVING

        elif self.state == self.STATE.IN_CITY:
            self.state = self.STATE.CHOOSE_ROAD


class ActionBattlePvE_1x1Prototype(ActionPrototype):

    TYPE = 'BATTLE_PVE_1x1'
    SHORT_DESCRIPTION = u'сражается'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        BATTLE_RUNNING = 'battle_running'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, mob):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       mob=s11n.to_json(mob.serialize()))
        return cls(model=model)

    def bit_mob(self, percents):

        if self.state != self.STATE.BATTLE_RUNNING:
            return False

        self.mob.striked_by(percents)
        self.percents = 1.0 - self.mob.health

        return True

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.hero.push_message(msg_generator.msg_action_battlepve1x1_start(self.hero, self.mob))
            self.state = self.STATE.BATTLE_RUNNING

        elif self.state == self.STATE.BATTLE_RUNNING:

            if self.hero.context.leave_battle():
                self.percents = 1
                self.state = self.STATE.PROCESSED

            elif self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0

            else:
                self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)

                hero_initiative = random.uniform(0, self.hero.battle_speed + self.mob.battle_speed)

                if hero_initiative < self.hero.battle_speed:

                    if random.uniform(0, 1) <= heroes_settings.USE_ABILITY_CHANCE:
                        self.hero.trigger_ability(HERO_ABILITIES_EVENTS.STRIKE_MOB)

                    damage = self.mob.strike_by_hero(self.hero)

                    self.hero.context.after_hero_strike()

                    self.hero.push_message(msg_generator.msg_action_battlepve1x1_hero_strike_mob(self.hero, self.mob, damage))

                else:
                    
                    if not self.hero.context.skip_mob_strike():
                        damage = self.mob.strike_hero(self.hero)
                        
                        self.hero.push_message(msg_generator.msg_action_battlepve1x1_mob_strike_hero(self.hero, self.mob, damage))
                    else:
                        self.hero.push_message(msg_generator.msg_action_battlepve1x1_mob_mis_by_hero(self.hero, self.mob))

                    self.hero.context.after_mob_strike()


                if self.hero.health <= 0:
                    self.hero.kill(self)
                    self.hero.push_message(msg_generator.msg_action_battlepve1x1_hero_killed(self.hero, self.mob))
                    self.state = self.STATE.PROCESSED

                if self.mob.health <= 0:
                    self.mob.kill()
                    self.hero.add_experience(EXPERIENCE_VALUES.FOR_KILL)
                    self.hero.push_message(msg_generator.msg_action_battlepve1x1_mob_killed(self.hero, self.mob))

                    loot = self.mob.get_loot(self.hero.chaoticity)
                    self.hero.put_loot(loot)

                    self.state = self.STATE.PROCESSED

                self.percents = 1.0 - self.mob.health
                
            if self.state == self.STATE.PROCESSED:
                self.remove_mob()
                self.hero.context.after_battle_end()

class ActionResurrectPrototype(ActionPrototype):

    TYPE = 'RESURRECT'
    SHORT_DESCRIPTION = u'воскресает'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        RESURRECT = 'resurrect'

    @classmethod
    @nested_commit_on_success
    def create(cls, parent):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model, 
                                       order=parent.order+1)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.RESURRECT

        elif self.state == self.STATE.RESURRECT:
            self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)
            self.percents = min(1, float(self.entropy) / self.ENTROPY_BARRIER)

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
                self.percents = 1.0
                self.hero.resurrent()
                self.state = self.STATE.PROCESSED
                
                # self.hero.save()


class ActionInPlacePrototype(ActionPrototype):

    TYPE = 'IN_PLACE'
    SHORT_DESCRIPTION = u'изучает окрестности'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        TRADING = 'trading'
        RESTING = 'resting'
        EQUIPPING = 'equipping'

    @property
    def can_rest_in_town(self):
        return self.state in [self.STATE.UNINITIALIZED]

    @property
    def can_equip_in_town(self):
        return self.state in [self.STATE.UNINITIALIZED, self.STATE.RESTING]

    @property
    def can_trade_in_town(self):
        return self.state in [self.STATE.UNINITIALIZED, self.STATE.RESTING, self.STATE.EQUIPPING]

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, settlement):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model, 
                                       hero=parent.hero.model, 
                                       order=parent.order+1,
                                       place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.place.is_settlement:
            return self.process_settlement()

    def process_settlement(self):

        if self.can_rest_in_town and self.hero.need_rest_in_town:
            self.state = self.STATE.RESTING
            self.bundle.add_action(ActionRestInSettlementPrototype.create(self, self.place))

        elif self.can_equip_in_town and self.hero.need_equipping_in_town:
            self.state = self.STATE.EQUIPPING

            self.bundle.add_action(ActionEquipInSettlementPrototype.create(self, self.place))

        elif self.can_trade_in_town and self.hero.need_trade_in_town:
            self.state = self.STATE.TRADING

            self.bundle.add_action(ActionTradeInSettlementPrototype.create(self, self.place))
            
        else:
            self.state = self.STATE.PROCESSED


class ActionRestInSettlementPrototype(ActionPrototype):

    TYPE = 'REST_IN_SETTLEMENT'
    SHORT_DESCRIPTION = u'отдыхает'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        RESTING = 'resting'

    settlement_id = ActionPrototype.place_id
    settlement = ActionPrototype.place

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, settlement):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model, 
                                       order=parent.order+1, 
                                       place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.RESTING
            self.percents = 0
            self.hero.push_message(msg_generator.msg_action_restinsettlement_start(self.hero))

        elif self.state == self.STATE.RESTING:

            heal_amount = heal_in_town(self.hero)

            if random.uniform(0, 1) < 0.33:
                self.hero.push_message(msg_generator.msg_action_restinsettlement_resring(self.hero, heal_amount))

            self.percents = float(self.hero.health/self.hero.max_health)

            if self.hero.health == self.hero.max_health:
                self.state = self.STATE.PROCESSED


class ActionEquipInSettlementPrototype(ActionPrototype):

    TYPE = 'EQUIP_IN_SETTLEMENT'
    SHORT_DESCRIPTION = u'экипируется'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        EQUIPPING = 'equipping'

    settlement_id = ActionPrototype.place_id
    settlement = ActionPrototype.place

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, settlement):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model, 
                                       order=parent.order+1, 
                                       place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.EQUIPPING
            self.percents = 0
            self.hero.push_message(msg_generator.msg_action_equipinsettlement_start(self.hero))

        elif self.state == self.STATE.EQUIPPING:
            unequipped, equipped = equip_in_city(self.hero)
            if equipped:
                if unequipped:
                    self.hero.push_message(msg_generator.msg_action_equipinsettlement_change_item(self.hero, unequipped, equipped))
                else:
                    self.hero.push_message(msg_generator.msg_action_equipinsettlement_equip_item(self.hero, equipped))
            else:
                self.equipped = True
                self.state = self.STATE.PROCESSED


class ActionTradeInSettlementPrototype(ActionPrototype):

    TYPE = 'TRADE_IN_SETTLEMENT'
    SHORT_DESCRIPTION = u'торгует'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        TRADING = 'trading'

    settlement_id = ActionPrototype.place_id
    settlement = ActionPrototype.place

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        info = super(ActionTradeInSettlementPrototype, self).ui_info()
        info['data'] = {'hero_id': self.hero_id,
                        'settlement': self.settlement_id }
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, settlement):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.TRADING
            self.percents = 0
            self.hero.push_message(msg_generator.msg_action_tradeinsettlement_start(self.hero))

        elif self.state == self.STATE.TRADING:
            quest_items_count, loot_items_count = self.hero.bag.occupation
            if loot_items_count:

                for item in self.hero.bag.items():
                    artifact_uuid, artifact = item
                    if not artifact.quest:
                        break
                    
                sell_price = sell_in_city(self.hero, artifact, False)

                self.hero.push_message(msg_generator.msg_action_tradeinsettlement_sell_item(self.hero, artifact, sell_price))
            else:
                self.state = self.STATE.PROCESSED


class ActionMoveNearPlacePrototype(ActionPrototype):

    TYPE = 'MOVE_NEAR_PLACE'
    SHORT_DESCRIPTION = u'бродит по окрестностям'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        MOVING = 'MOVING'
        BATTLE = 'BATTLE'

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        info = super(ActionMoveNearPlacePrototype, self).ui_info()
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, place, back):
        parent.leader = False

        if back:
            x, y = place.x, place.y
        else:
            x, y = random.choice(place.nearest_cells)

        model = Action.objects.create( type=cls.TYPE, 
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       place=place.model,
                                       destination_x=x,
                                       destination_y=y)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.MOVING
            self.percents = 0

            dest_x, dest_y = self.get_destination()

            if self.hero.position.is_walking:
                from_x, from_y = self.hero.position.coordinates_to
                self.hero.position.set_coordinates(from_x, from_y, dest_x, dest_y, percents=0)
            else:
                self.hero.position.set_coordinates(self.place.x, self.place.y, dest_x, dest_y, percents=0)

        elif self.state == self.STATE.MOVING:

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
                mob = create_mob_for_hero(self.hero)

                self.bundle.add_action(ActionBattlePvE_1x1Prototype.create(parent=self, mob=mob))

                self.state = self.STATE.BATTLE

            else:
                self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)

                if random.uniform(0, 1) < 0.2:
                    self.hero.push_message(msg_generator.msg_action_movenearplace_walk(self.hero, self.place))
            
                if self.hero.position.subroad_len() == 0:
                    self.hero.position.percents += 0.1
                else:
                    delta = self.hero.move_speed / self.hero.position.subroad_len()
                    self.hero.position.percents += delta

                self.percents = self.hero.position.percents

                if self.hero.position.percents >= 1:
                    self.hero.position.percents = 1
                    self.percents = 1

                    to_x, to_y = self.hero.position.coordinates_to
                    if self.place.x == to_x and self.place.y == to_y:
                        self.hero.position.set_place(self.place)

                    self.state = self.STATE.PROCESSED

        elif self.state == self.STATE.BATTLE:
            self.state = self.STATE.MOVING


ACTION_TYPES = get_actions_types()
