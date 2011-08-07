# -*- coding: utf-8 -*-
import random

from django_next.utils.decorators import nested_commit_on_success

from ..heroes.prototypes import get_hero_by_model
from ..heroes.logic import create_npc_for_hero, strike
from ..map.places.prototypes import PlacePrototype
from ..map.roads.prototypes import RoadPrototype, get_road_between

from .models import Action, ActionIdleness, ActionMoveTo, ActionBattlePvE_1x1, ActionResurrect, ActionQuest

#TODO: change relations between action from "parent control children" to "parent respond to children messages"
#      in this case parent actions should not store link to child, and should not be processed,  
#      until child send to parent message

def get_actions_types():
    actions = {}
    for key, cls in globals().items():
        if isinstance(cls, type) and issubclass(cls, ActionPrototype) and cls != ActionPrototype:
            actions[cls.TYPE] = cls
    return actions

def get_action_by_model(base_model, model=None):
    if base_model is None: 
        return None

    return ACTION_TYPES[base_model.type](base_model=base_model, model=model)


class ActionPrototype(object):

    TYPE = 'BASE'
    SHORT_DESCRIPTION = 'undefined'
    ENTROPY_BARRIER = 100

    def __init__(self, base_model, *argv, **kwargs):
        super(ActionPrototype, self).__init__(*argv, **kwargs)
        self.base_model = base_model

    @property
    def id(self): return self.base_model.id

    @property
    def type(self): return self.base_model.type

    def get_percents(self): return self.base_model.percents
    def set_percents(self, value): self.base_model.percents = value
    percents = property(get_percents, set_percents)

    def get_state(self): return self.base_model.state
    def set_state(self, value): self.base_model.state = value
    state = property(get_state, set_state)

    def get_entropy(self): return self.base_model.entropy
    def set_entropy(self, value): self.base_model.entropy = value
    entropy = property(get_entropy, set_entropy)

    @property
    def STATE(self): return self.model.STATE

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.base_model.delete()
    def save(self): self.base_model.save()

    def ui_info(self):
        return {'id': self.id,
                'type': self.type,
                'short_description': self.SHORT_DESCRIPTION,
                'percents': self.percents,
                'entropy': self.entropy,
                'entropy_barier': self.ENTROPY_BARRIER}


class ActionIdlenessPrototype(ActionPrototype):

    TYPE = 'IDLENESS'
    SHORT_DESCRIPTION = u'бездельничает'

    ENTROPY_BARRIER = 100

    def __init__(self, base_model, model=None, *argv, **kwargs):
        super(ActionIdlenessPrototype, self).__init__(base_model, *argv, **kwargs)
        self.model = model if model else base_model.action_idleness

    def get_entropy_action(self):
        if not hasattr(self, '_entropy_action'):
            self._entropy_action = get_action_by_model(base_model=self.model.entropy_action)
        return self._entropy_action
    def set_entropy_action(self, value):
        if hasattr(self, '_entropy_action'):
            delattr(self, '_entropy_action')
        self.model.entropy_action = value.base_model if value else None
    entropy_action = property(get_entropy_action, set_entropy_action)

    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        self.model.delete()
        super(ActionIdlenessPrototype, self).remove()

    def save(self):
        self.model.save()
        super(ActionIdlenessPrototype, self).save()

    def ui_info(self):
        info = super(ActionIdlenessPrototype, self).ui_info()
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, hero):
        base_model = Action.objects.create( type=cls.TYPE, percents=0.0)
        
        model = ActionIdleness.objects.create( base_action=base_model, hero=hero.model)

        action = cls(base_model=base_model, model=model)

        hero.push_action(action)
        hero.save()

        return action

    def process(self):

        hero = get_hero_by_model(self.model.hero)

        if self.entropy_action:
            if self.entropy_action.state == self.entropy_action.STATE.PROCESSED:
                self.entropy_action.remove()
                self.entropy_action = None
            else:
                return

        if not self.entropy_action and not hero.is_alive:         
            
            if hero.is_npc:
                return

            self.entropy = 0
            self.entropy_action = ActionResurrectPrototype.create(hero=hero)
            self.save()
            return


        if self.entropy >= self.ENTROPY_BARRIER:
            from ..quests.logic import create_random_quest_for_hero

            self.entropy = 0
            hero.create_tmp_log_message('Entropy filled, receiving new quest')
            quest = create_random_quest_for_hero(hero)
            action = quest.create_action()
            self.entropy_action = action

        else:
            self.entropy = self.entropy + random.randint(1, hero.chaoticity)

            self.percents = float(self.entropy) / self.ENTROPY_BARRIER

            hero.create_tmp_log_message('do nothing')

        self.save()


class ActionQuestPrototype(ActionPrototype):

    TYPE = 'QUEST'
    SHORT_DESCRIPTION = u'выполняет задание'

    def __init__(self, base_model, model=None, *argv, **kwargs):
        super(ActionQuestPrototype, self).__init__(base_model, *argv, **kwargs)
        self.model = model if model else base_model.action_quest

    @property
    def quest(self):
        from ..quests.prototypes import get_quest_by_model
        if not hasattr(self, '_quest'):
            self._quest = get_quest_by_model(base_model=self.model.quest)
        return self._quest

    def get_quest_action(self): 
        if not hasattr(self, '_quest_action'):
            self._quest_action = None
            if self.model.quest_action:
                self._quest_action = get_action_by_model(base_model=self.model.quest_action)
        return self._quest_action
    def set_quest_action(self, value): 
        if hasattr(self, '_quest_action'):
            delattr(self, '_quest_action')
        self.model.quest_action = value.base_model if value else None
    quest_action = property(get_quest_action, set_quest_action)

    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        super(ActionQuestPrototype, self).remove()

    def save(self):
        self.model.save()
        super(ActionQuestPrototype, self).save()

    def ui_info(self):
        info = super(ActionQuestPrototype, self).ui_info()
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, quest):
        base_model = Action.objects.create( type=cls.TYPE, percents=0.0)
        
        model = ActionQuest.objects.create( base_action=base_model, 
                                            quest=quest.base_model)

        action = cls(base_model=base_model, model=model)

        for hero in quest.heroes:
            hero.push_action(action)
            hero.save()

        return action

    def process(self):

        if not self.quest.hero.is_alive:
            self.quest.remove()
            self.state = self.STATE.PROCESSED
            if self.quest_action:
                self.quest_action.remove()
            self.save()
            return

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.PROCESSING
        
        if self.state == self.STATE.PROCESSING:
            finish, percents = self.quest.process(self)
            self.percents = percents
            if finish:
                self.state = self.STATE.PROCESSED
                self.quest.remove()

        self.save()

        if self.state != self.STATE.PROCESSED:
            self.quest.save()


class ActionMoveToPrototype(ActionPrototype):

    TYPE = 'MOVE_TO'
    SHORT_DESCRIPTION = u'путешествует'

    ENTROPY_BARRIER = 35

    def __init__(self, base_model, model=None, *argv, **kwargs):
        super(ActionMoveToPrototype, self).__init__(base_model, *argv, **kwargs)
        self.model = model if model else base_model.action_move_to

    @property
    def road_id(self): return self.model.road_id

    @property
    def destination_id(self): return self.model.destination_id

    @property
    def destination(self):
        if not hasattr(self, '_destination'):
            self._destination = PlacePrototype(model=self.model.destination)
        return self._destination

    def get_road(self):
        if not hasattr(self, '_road'):
            self._road = RoadPrototype(model=self.model.road)
        return self._road
    def set_road(self, value):
        if hasattr(self, '_road'):
            delattr(self, '_road')
        self.model.road = value.model
    road = property(get_road, set_road)

    def get_entropy_action(self):
        if not hasattr(self, '_entropy_action'):
            self._entropy_action = get_action_by_model(base_model=self.model.entropy_action)
        return self._entropy_action
    def set_entropy_action(self, value):
        if hasattr(self, '_entropy_action'):
            delattr(self, '_entropy_action')
        self.model.entropy_action = value.base_model if value else None
    entropy_action = property(get_entropy_action, set_entropy_action)

    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = get_hero_by_model(self.model.hero)
        return self._hero

    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        self.model.delete()
        super(ActionMoveToPrototype, self).remove()

    def save(self):
        self.model.save()
        super(ActionMoveToPrototype, self).save()

    def ui_info(self):
        info = super(ActionMoveToPrototype, self).ui_info()
        info['data'] = {'destination': self.destination_id,
                        'road': self.road_id}
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, hero, destination):
        base_model = Action.objects.create( type=cls.TYPE, 
                                            percents=0.0)
        
        model = ActionMoveTo.objects.create( base_action=base_model, 
                                             hero=hero.model,
                                             destination=destination.model)

        action = cls(base_model=base_model, model=model)

        hero.push_action(action)
        hero.save()

        return action

    @nested_commit_on_success
    def process(self):

        position = self.hero.position

        if self.entropy_action:
            if self.entropy_action.state != self.STATE.PROCESSED:
                return
            else:
                self.entropy_action.remove()
                self.entropy_action = None

                if not self.hero.is_alive:
                    self.state = self.STATE.PROCESSED

        if self.state == self.STATE.UNINITIALIZED:
            if self.hero.position.place.id != self.destination.id:
                self.road = get_road_between(self.hero.position.place, self.destination)
                position.set_road(self.road, invert=self.hero.position.place.id != self.road.point_1_id)
                self.state = self.STATE.MOVING
            else:
                self.percents = 1
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.MOVING:

            self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
                npc = create_npc_for_hero(self.hero)
                self.entropy_action = ActionBattlePvE_1x1Prototype.create(hero=self.hero, npc=npc)
            else:
                self.hero.create_tmp_log_message('I go, I go, I go to %s' % self.destination.name)
            
                delta = self.hero.move_speed / self.road.length

                position.percents += delta

                self.percents = position.percents

                if position.percents > 1:
                    position.set_place(self.destination)
                    self.state = self.STATE.PROCESSED

        position.save()
        self.save()


class ActionBattlePvE_1x1Prototype(ActionPrototype):

    TYPE = 'BATTLE_PVE_1x1'
    SHORT_DESCRIPTION = u'сражается'

    ENTROPY_BARRIER = 35

    def __init__(self, base_model, model=None, *argv, **kwargs):
        super(ActionBattlePvE_1x1Prototype, self).__init__(base_model, *argv, **kwargs)
        self.model = model if model else base_model.action_battle_pve_1x1

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = get_hero_by_model(self.model.hero)
        return self._hero

    @property
    def npc(self):
        if not hasattr(self, '_npc'):
            self._npc = get_hero_by_model(self.model.npc)
        return self._npc

    def get_hero_initiative(self): return self.model.hero_initiative
    def set_hero_initiative(self, value): self.model.hero_initiative = value
    hero_initiative = property(get_hero_initiative, set_hero_initiative)

    def get_npc_initiative(self): return self.model.npc_initiative
    def set_npc_initiative(self, value): self.model.npc_initiative = value
    npc_initiative = property(get_npc_initiative, set_npc_initiative)



    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        self.model.delete()
        super(ActionBattlePvE_1x1Prototype, self).remove()

    def save(self):
        self.model.save()
        super(ActionBattlePvE_1x1Prototype, self).save()

    def ui_info(self):
        info = super(ActionBattlePvE_1x1Prototype, self).ui_info()
        info['data'] = {'hero_id': self.hero_id,
                        'npc': self.npc.ui_info(ignore_actions=True)}
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, hero, npc):
        base_model = Action.objects.create( type=cls.TYPE, 
                                            percents=0.0)
        
        model = ActionBattlePvE_1x1.objects.create( base_action=base_model, 
                                                    hero=hero.model,
                                                    npc=npc.model)

        action = cls(base_model=base_model, model=model)

        hero.push_action(action)
        hero.save()

        npc.push_action(action)
        npc.save()

        return action

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.hero.create_tmp_log_message('start battle with NPC')
            self.hero_initiative = self.hero.battle_speed
            self.npc_initiative = self.npc.battle_speed
            self.state = self.STATE.BATTLE_RUNNING

        if self.state == self.STATE.BATTLE_RUNNING:
            self.entropy = self.entropy + random.randint(1, self.hero.chaoticity + self.npc.chaoticity)

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
            else:
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
            self.state = self.STATE.PROCESSED

        self.percents = max(0, float(self.npc.max_health - self.npc.health) / self.npc.max_health)

        self.hero.save()
        self.npc.save()

        self.save()


class ActionResurrectPrototype(ActionPrototype):

    TYPE = 'RESURRECT'
    SHORT_DESCRIPTION = u'воскресает'

    ENTROPY_BARRIER = 35

    def __init__(self, base_model, model=None, *argv, **kwargs):
        super(ActionResurrectPrototype, self).__init__(base_model, *argv, **kwargs)
        self.model = model if model else base_model.action_resurrect

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = get_hero_by_model(self.model.hero)
        return self._hero

    ###########################################
    # Object operations
    ###########################################

    def remove(self): 
        self.model.delete()
        super(ActionResurrectPrototype, self).remove()

    def save(self):
        self.model.save()
        super(ActionResurrectPrototype, self).save()

    def ui_info(self):
        info = super(ActionResurrectPrototype, self).ui_info()
        info['data'] = {'hero_id': self.hero_id}
        return info

    @classmethod
    @nested_commit_on_success
    def create(cls, hero):

        base_model = Action.objects.create( type=cls.TYPE, 
                                            percents=0.0)
        
        model = ActionResurrect.objects.create( base_action=base_model, 
                                                hero=hero.model)

        action = cls(base_model=base_model, model=model)

        hero.push_action(action)
        hero.save()

        return action

    @nested_commit_on_success
    def process(self):

        if self.state == self.STATE.UNINITIALIZED:
            self.state = self.STATE.RESURRECT

        if self.state == self.STATE.RESURRECT:
            self.entropy = self.entropy + random.randint(1, self.hero.chaoticity)

            if self.entropy >= self.ENTROPY_BARRIER:
                self.entropy = 0
                self.percents = 1.0
                self.hero.resurrent()
                self.state = self.STATE.PROCESSED
            else:
                self.percents = float(self.entropy) / self.ENTROPY_BARRIER

        self.hero.save()
        self.save()


ACTION_TYPES = get_actions_types()
