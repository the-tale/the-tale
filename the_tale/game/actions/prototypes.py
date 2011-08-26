# -*- coding: utf-8 -*-
import random

from django_next.utils.decorators import nested_commit_on_success
from django_next.utils import s11n

from ..heroes.prototypes import get_hero_by_model
from ..heroes.logic import create_npc_for_hero, strike, heal_in_town, sell_in_city, equip_in_city
from ..map.places.prototypes import get_place_by_model
from ..map.roads.prototypes import get_road_by_model, WaymarkPrototype

from .models import Action
from . import models as action_models

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
        UNINITIALIZED = 'uninitialized'
        PROCESSED = 'processed'

    def __init__(self, model, *argv, **kwargs):
        super(ActionPrototype, self).__init__(*argv, **kwargs)
        self.model = model
        self.removed = False

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type

    @property
    def order(self): return self.model.order

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
        if not hasattr(self, '_hero'):
            self._hero = get_hero_by_model(self.model.hero)
        return self._hero

    def get_child_action(self):
        if not hasattr(self, '_child_action'):
            self._child_action = get_action_by_model(model=self.model.child_action)
        return self._child_action
    def set_child_action(self, value):
        if hasattr(self, '_child_action'):
            delattr(self, '_child_action')
        self.model.child_action = value.model if value else None
    child_action = property(get_child_action, set_child_action)

    @property
    def road_id(self): return self.model.road_id

    @property
    def place_id(self): return self.model.destination_id

    @property
    def place(self):
        if not hasattr(self, '_place'):
            self._place = get_place_by_model(model=self.model.place)
        return self._destination

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
    def npc(self):
        if not hasattr(self, '_npc'):
            self._npc = get_hero_by_model(self.model.npc)
        return self._npc

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        self.model.delete()
        self.removed = True

    def save(self): 
        if hasattr(self, '_data'):
            self.model.data = s11n.to_json(self._data)
        self.model.save()

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
                             'npc_id': self.npc_id},
                'data': self.data #TODO: get json directly from self.model.data, without reloading it
                }

    def process_action(self):

        if self.child_action:
            if self.child_action.state != self.child_action.STATE.PROCESSED:
                raise ActionException("Action %d called before child action finish it's work")

            self.child_action.remove()
            self.child_action = None
            self.leader = True

        self.process()

        if not self.removed:
            self.save()

class ActionIdlenessPrototype(ActionPrototype):

    TYPE = 'IDLENESS'
    SHORT_DESCRIPTION = u'бездельничает'
    ENTROPY_BARRIER = 100

    ###########################################
    # Object operations
    ###########################################

    def on_die(self):
        self.child_action = ActionResurrectPrototype.create(self)
        return True

    @classmethod
    @nested_commit_on_success
    def create(cls, parent):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True)
        return cls(model=model)

    def process(self):

        self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)
        self.percents = float(self.entropy) / self.ENTROPY_BARRIER
        self.hero.create_tmp_log_message('do nothing')

        if (self.entropy >= self.ENTROPY_BARRIER / 2 and 
            (self.hero.need_trade_in_town or self.hero.need_rest_in_town) and 
            self.hero.position.is_settlement):
            self.child_action = action_models.ActionInPlacePrototype.create(self, self.hero.position.place)

        elif self.entropy >= self.ENTROPY_BARRIER:
            from ..quests.logic import create_random_quest_for_hero

            self.entropy = 0
            self.hero.create_tmp_log_message('Entropy filled, receiving new quest')
            quest = create_random_quest_for_hero(self.hero)
            self.child_action = quest.create_action(self)


class ActionQuestPrototype(ActionPrototype):

    TYPE = 'QUEST'
    SHORT_DESCRIPTION = u'выполняет задание'

    class STATE(ActionPrototype.STATE):
        PROCESSING = 'processing'

    @property
    def quest(self):
        from ..quests.prototypes import get_quest_by_model
        if not hasattr(self, '_quest'):
            self._quest = get_quest_by_model(model=self.model.quest)
        return self._quest

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, quest):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.parent_order+1, leader=True, quest=quest.model)
        return cls(model=model)

    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.PROCESSING
        
        elif self.state == self.STATE.PROCESSING:
            finish, percents = self.quest.process(self)
            self.percents = percents
            if finish:
                self.state = self.STATE.PROCESSED
                self.quest.remove()
            else:
                self.quest.save()


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
    def create(cls, parent, destination):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.parent_order+1, leader=True, place=destination.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.child_action:
            self.child_action.remove()
            self.child_action = None

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.CHOOSE_ROAD

        elif self.state == self.STATE.CHOOSE_ROAD:
            if self.hero.position.place_id != self.destination_id:
                self.road = WaymarkPrototype.look_for_road(point_from=self.hero.position.place_id, point_to=self.destination_id)
                self.hero.position.set_road(self.road, invert=(self.hero.position.place_id != self.road.point_1_id))
                self.state = self.STATE.MOVING
            else:
                self.percents = 1
                self.state = self.STATE.PROCESSED

        elif self.state == self.STATE.MOVING:

            current_destination = self.road.point_2 if not self.hero.position.invert_direction else self.road.point_1

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
                npc = create_npc_for_hero(self.hero)
                self.state = self.STATE.BATTLE
                self.child_action = ActionBattlePvE_1x1Prototype.create(parent=self, npc=npc)
            else:
                self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)

                self.hero.create_tmp_log_message('I go, I go, I go to %s' % current_destination.name)
            
                delta = self.hero.move_speed / self.road.length

                self.hero.position.percents += delta

                self.percents = self.hero.position.percents

                if self.hero.position.percents >= 1:
                    self.hero.position.percents = 1
                    self.hero.position.set_place(current_destination)
                    
                    self.state = self.STATE.IN_CITY
                    self.child_action = action_models.ActionInCityPrototype.create(parent=self, settlement=current_destination)


        elif self.state == self.STATE.BATTLE:
            self.state = self.STATE.MOVING

        elif self.state == self.STATE.IN_CITY:
            self.state = self.STATE.CHOOSE_ROAD

        self.hero.position.save()


class ActionBattlePvE_1x1Prototype(ActionPrototype):

    TYPE = 'BATTLE_PVE_1x1'
    SHORT_DESCRIPTION = u'сражается'
    ENTROPY_BARRIER = 35

    class STATE(ActionPrototype.STATE):
        BATTLE_RUNNING = 'battle_running'

    def get_hero_initiative(self): return self.data['hero_initiative']
    def set_hero_initiative(self, value): self.data['hero_initiative'] = value
    hero_initiative = property(get_hero_initiative, set_hero_initiative)

    def get_npc_initiative(self): return self.data['npc_initiative']
    def set_npc_initiative(self, value): self.data['npc_initiative'] = value
    npc_initiative = property(get_npc_initiative, set_npc_initiative)

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    @nested_commit_on_success
    def create(cls, parent, npc):
        parent.leader = False
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True, npc=npc.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.hero.create_tmp_log_message('start battle with NPC')
            self.hero_initiative = self.hero.battle_speed
            self.npc_initiative = self.npc.battle_speed
            self.state = self.STATE.BATTLE_RUNNING

        elif self.state == self.STATE.BATTLE_RUNNING:

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
            else:
                self.entropy = self.entropy + random.randint(1, self.hero.chaoticity + self.npc.chaoticity)

                if self.hero_initiative >= self.npc_initiative:
                    self.npc_initiative += self.npc.battle_speed
                    strike_result = strike(self.hero, self.npc)
                else:
                    self.hero_initiative += self.hero.battle_speed
                    strike_result = strike(self.npc, self.hero)

                self.hero.create_tmp_log_message('%(attaker)s bit %(defender)s for %(damage)s HP' % {'attaker': strike_result.attaker.name,
                                                                                                     'defender': strike_result.defender.name,
                                                                                                     'damage': strike_result.damage})
                if self.hero.health <= 0:
                    self.hero.kill()
                    self.npc.kill()
                    self.hero.create_tmp_log_message('Hero was killed')
                    self.state = self.STATE.PROCESSED

                if self.npc.health <= 0:
                    self.npc.kill()
                    self.hero.create_tmp_log_message('NPC was killed')

                    #generate loot
                    from ..artifacts.constructors import generate_loot, TEST_LOOT_LIST
                    loot = generate_loot(TEST_LOOT_LIST, 1, 4.5, 1.5, self.hero.chaoticity)
                    self.hero.put_loot(loot)

                    self.state = self.STATE.PROCESSED

                self.percents = min(1, max(0, float(self.npc.max_health - self.npc.health) / self.npc.max_health))

                self.hero.save()
                self.npc.save()

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
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True)
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
                
                self.hero.save()


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
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True, place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.place.is_settlement:
            return self.process_settlement()

    def process_settlement(self):

        if self.can_rest_in_town and self.hero.need_rest_in_town:
            self.state = self.STATE.RESTING
            self.child_action = ActionRestInSettlementPrototype.creat(self, self.place)
            self.hero.create_tmp_log_message('hero decided to have a rest')

        elif self.can_equip_in_town and self.hero.need_equipping_in_town:
            self.state = self.STATE.EQUIPPING
            self.child_action = ActionEquipInSettlementPrototype.creat(self, self.place)
            self.hero.create_tmp_log_message('hero looking for new equipment in his bag')

        elif self.can_trade_in_town and self.hero.need_trade_in_town:
            self.state = self.STATE.TRADING
            self.child_action = ActionTradeInSettlementPrototype.creat(self, self.place)
            self.hero.create_tmp_log_message('hero decided to sell all loot')        
            
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
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True, place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.RESTING
            self.percents = 0

        elif self.state == self.STATE.RESTING:

            heal_amount = heal_in_town(self.hero)
            self.hero.create_tmp_log_message('hero healed for %d HP' % heal_amount)

            self.percents = float(self.hero.health/self.hero.max_health)

            if self.hero.health == self.hero.max_health:
                self.hero.create_tmp_log_message('hero is completly healthty')
                self.state = self.STATE.PROCESSED
                self.hero.save()


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
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True, place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.EQUIPING
            self.percents = 0

        elif self.state == self.STATE.EQUIPING:
            unequipped, equipped = equip_in_city(self.hero)
            if equipped:
                if unequipped:
                    self.hero.create_tmp_log_message('hero change "%s" to "%s"' % (unequipped.name, equipped.name))
                else:
                    self.hero.create_tmp_log_message('hero equip "%s"' % equipped.name)
            else:
                self.equipped = True
                self.state = self.STATE.PROCESSED
                self.hero.save()


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
        model = Action.objects.create( type=cls.TYPE, percents=0.0, hero=parent.hero_id, order=parent.order+1, leader=True, place=settlement.model)
        return cls(model=model)

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.TRADING
            self.percents = 0

        elif self.state == self.STATE.TRADING:
            quest_items_count, loot_items_count = self.hero.bag.occupation
            if loot_items_count:

                items = self.hero.bag.items()
                artifact_uuid, artifact = items[0]
                    
                sell_price = sell_in_city(self.hero, artifact_uuid, False)

                self.hero.create_tmp_log_message('hero solled %s for %d g.' % (artifact.name, sell_price) )

            else:
                self.hero.create_tmp_log_message('hero has solled all what he wants')
                self.state = self.STATE.PROCESSED
                self.hero.save()


ACTION_TYPES = get_actions_types()
