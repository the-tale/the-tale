# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from game.journal_messages.prototypes import MessagesLogPrototype, get_messages_log_by_model

from game.map.places.prototypes import HeroPositionPrototype, PlacePrototype

from .models import Hero, HeroAction
from . import game_info

attrs = game_info.attributes

def get_hero_by_id(model_id):
    hero = Hero.objects.get(id=model_id)
    return HeroPrototype(model=hero)

def get_hero_by_model(model):
    return HeroPrototype(model=model)

def get_heroes_by_query(query):
    return [ get_hero_by_model(hero) for hero in list(query)]


class HeroPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @property
    def is_npc(self): return self.model.npc

    def get_is_alive(self): return self.model.alive
    def set_is_alive(self, value): self.model.alive = value
    is_alive = property(get_is_alive, set_is_alive)

    @property
    def id(self): return self.model.id

    @property
    def angel_id(self): return self.model.angel_id

    ###########################################
    # Base attributes
    ###########################################

    @property
    def first(self): return self.model.first

    @property
    def name(self): return self.model.name

    @property
    def wisdom(self): return self.model.wisdom

    def get_health(self): return self.model.health
    def set_health(self, value): self.model.health = value
    health = property(get_health, set_health)

    ###########################################
    # Primary attributes
    ###########################################

    @property
    def intellect(self): return self.model.intellect
    @property
    def constitution(self): return self.model.constitution
    @property
    def reflexes(self): return self.model.reflexes
    @property
    def chaoticity(self): return self.model.chaoticity

    ###########################################
    # accumulated attributes
    ###########################################

    ###########################################
    # Secondary attributes
    ###########################################

    @property
    def move_speed(self): return game_info.attributes.secondary.move_speed.get(self)

    @property
    def battle_speed(self): return game_info.attributes.secondary.battle_speed.get(self)

    @property
    def max_health(self): return game_info.attributes.secondary.max_health.get(self)

    @property
    def min_damage(self): return game_info.attributes.secondary.min_damage.get(self)

    @property
    def max_damage(self): return game_info.attributes.secondary.max_damage.get(self)

    ###########################################
    # actions
    ###########################################

    @property
    def actions(self):
        from game.actions.prototypes import ACTION_TYPES

        if not hasattr(self, '_actions'):
            self._actions = []
            hero_actions = HeroAction.objects.select_related('action').filter(hero=self.model).order_by('order')
            actions = [ hero_action.action for hero_action in hero_actions]
            for action in actions:
                action_object = ACTION_TYPES[action.type](base_model=action)
                self._actions.append(action_object)

        return self._actions

    def push_action(self, action):
        HeroAction.objects.create(hero=self.model,
                                  action=action.base_model,
                                  order=len(self.actions) )
        if hasattr(self, '_actions'):
            delattr(self, '_actions')

    def get_current_action(self): return self.actions[-1]

    @property
    def position(self):
        if not hasattr(self, '_position'):
            self._position = HeroPositionPrototype(model=self.model.position)
        return self._position


    def create_tmp_log_message(self, text):
        messages_log = self.get_messages_log()
        messages_log.push_message('TMP', 'TMP: %s' % text)
        messages_log.save()


    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): self.model.save()

    def get_messages_log(self):
        return get_messages_log_by_model(model=self.model.messages_log)

    def ui_info(self, ignore_actions=False):
        return {'id': self.id,
                'npc': self.is_npc,
                'angel': self.angel_id,
                'actions': [ action.ui_info() for action in self.actions ] if not ignore_actions else [],
                'messages': self.get_messages_log().messages,
                'position': self.position.ui_info(),
                'alive': self.is_alive,
                'base': { 'name': self.name,
                          'first': self.first,
                          'wisdom': self.wisdom,
                          'health': self.health,
                          'max_health': self.max_health},
                'primary': { 'intellect': self.intellect,
                             'constitution': self.constitution,
                             'reflexes': self.reflexes,
                             'chaoticity': self.chaoticity },
                'accumulated': { }
                }


    @classmethod
    @nested_commit_on_success
    def create(cls, angel, name, first, intellect, constitution, reflexes, chaoticity, npc=False):
        from game.actions.prototypes import ActionIdlenessPrototype

        hero = Hero.objects.create(angel=angel,
                                   npc=npc,

                                   name=name,
                                   first=first,

                                   health=attrs.secondary.max_health.from_attrs(constitution, 
                                                                                attrs.base.wisdom.initial),
                                   
                                   wisdom=attrs.base.wisdom.initial,

                                   intellect=intellect,
                                   constitution=constitution,
                                   reflexes=reflexes,
                                   chaoticity=chaoticity)

        hero = cls(model=hero)

        action = ActionIdlenessPrototype.create(hero=hero)

        messages = MessagesLogPrototype.create(hero)

        start_place = PlacePrototype.random_place()

        position = HeroPositionPrototype.create(hero=hero, place=start_place)

        return hero

    ###########################################
    # Game operations
    ###########################################

    def kill(self):

        self.is_alive = False
        self.health = 1
        self.position.set_place(PlacePrototype.random_place())
        self.position.save()
        
        # if not self.is_npc:
        #     raise Exception('killed')
        #     for action in reversed(self.actions[1:]):
        #         action.remove()

    def resurrent(self):
        self.health = self.max_health
        self.is_alive = True

    ###########################################
    # Next turn operations
    ###########################################

    def next_turn_update(self, turn):
        pass
