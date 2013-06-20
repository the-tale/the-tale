# coding: utf-8
import copy

from common.utils.decorators import lazy_property
from common.utils.logic import random_value_by_priority

from game.prototypes import TimePrototype
from game.map.places.storage import places_storage
from game.mobs.prototypes import MobPrototype
from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution
from game.balance import constants as c


UNINITIALIZED_STATE = 'uninitialized'

class ActionBase(object):

    __slots__ = ( 'hero',
                  'percents',
                  'bundle_id',
                  'description',
                  'state',
                  'removed',
                  'storage',
                  'updated',
                  'created_at_turn',
                  'context',
                  'quest_id',
                  'place_id',
                  'mob',
                  'data',
                  'break_at',
                  'length',
                  'destination_x',
                  'destination_y',
                  'percents_barier',
                  'extra_probability',
                  'mob_context',
                  'textgen_id',
                  'hero_health_lost',
                  'back',
                  'meta_action_id')


    class STATE:
        UNINITIALIZED = UNINITIALIZED_STATE
        PROCESSED = 'processed'

    TYPE = 'BASE'
    TEXTGEN_TYPE = None
    CONTEXT_MANAGER = None
    EXTRA_HELP_CHOICES = set()

    def __init__(self,
                 hero,
                 bundle_id,
                 state,
                 percents=0.0,
                 type=None, # just for deserialization
                 created_at_turn=None,
                 context=None,
                 description=None,
                 quest_id=None,
                 place_id=None,
                 mob=None,
                 data=None,
                 break_at=None,
                 length=None,
                 destination_x=None,
                 destination_y=None,
                 percents_barier=None,
                 extra_probability=None,
                 mob_context=None,
                 textgen_id=None,
                 hero_health_lost=0,
                 back=False,
                 meta_action_id=None,):

        self.hero = hero

        self.description = description

        self.percents = percents

        self.bundle_id = bundle_id

        self.state = state

        self.removed = False
        self.storage = None
        self.updated = False

        self.created_at_turn = created_at_turn if created_at_turn is not None else TimePrototype.get_current_turn_number()

        self.context = context if context is None or isinstance(context, self.CONTEXT_MANAGER) else self.CONTEXT_MANAGER.deserialize(context)
        self.mob_context = mob_context if mob_context is None or isinstance(mob_context, self.CONTEXT_MANAGER) else self.CONTEXT_MANAGER.deserialize(mob_context)

        self.quest_id = quest_id
        self.place_id = place_id

        self.mob = mob if mob is None or isinstance(mob, MobPrototype) else MobPrototype.deserialize(mob)

        self.data = data
        self.break_at = break_at
        self.length = length
        self.destination_x = destination_x
        self.destination_y = destination_y
        self.percents_barier = percents_barier
        self.extra_probability = extra_probability
        self.textgen_id = textgen_id
        self.hero_health_lost = 0
        self.back = back
        self.meta_action_id = meta_action_id


    def serialize(self):
        data = {'type': self.TYPE,
                'bundle_id': self.bundle_id,
                'state': self.state,
                'percents': self.percents,
                'description': self.description,
                'created_at_turn': self.created_at_turn}
        if self.context:
            data['context'] = self.context.serialize()
        if self.quest_id is not None:
            data['quest_id'] = self.quest_id
        if self.place_id is not None:
            data['place_id'] = self.place_id
        if self.mob:
            data['mob'] = self.mob.serialize()
        if self.data:
            data['data'] = self.data
        if self.break_at is not None:
            data['break_at'] = self.break_at
        if self.length is not None:
            data['length'] = self.length
        if self.destination_x is not None:
            data['destination_x'] = self.destination_x
        if self.destination_y is not None:
            data['destination_y'] = self.destination_y
        if self.percents_barier is not None:
            data['percents_barier'] = self.percents_barier
        if self.extra_probability is not None:
            data['extra_probability'] = self.extra_probability
        if self.mob_context:
            data['mob_context'] = self.mob_context.serialize()
        if self.textgen_id is None:
            data['textgen_id'] = self.textgen_id
        if self.hero_health_lost != 0:
            data['hero_health_lost'] = self.hero_health_lost
        if not self.back:
            data['back'] = self.back
        if self.meta_action_id is not None:
            data['meta_action_id'] = self.meta_action_id

        return data

    @classmethod
    def deserialize(cls, hero, data):
        return cls(hero=hero, **data)

    def ui_info(self):
        return {'percents': self.percents,
                'description': self.description,
                'info_link': self.info_link if hasattr(self, 'info_link') else None}

    @property
    def leader(self):
        return (not self.removed) and (self.hero.actions.current_action is self)

    def set_storage(self, storage):
        self.storage = storage

    @property
    def place(self): return places_storage[self.place_id]

    def remove_mob(self):
        self.mob = None

    @lazy_property
    def quest(self):
        from game.quests.prototypes import QuestPrototype
        if self.quest_id:
            return QuestPrototype.get_by_id(self.quest_id)
        return None

    def get_destination(self): return self.destination_x, self.destination_y
    def set_destination(self, x, y):
        self.destination_x = x
        self.destination_y = y

    @property
    def meta_action(self): return self.storage.meta_actions[self.meta_action_id] if self.meta_action_id else None

    @property
    def help_choices(self):
        choices = copy.copy(self.EXTRA_HELP_CHOICES)
        choices.add(c.HELP_CHOICES.MONEY)

        if self.hero.is_alive:
            if ((c.ANGEL_HELP_HEAL_IF_LOWER_THEN * self.hero.max_health > self.hero.health) or
                (self.hero.health < self.hero.max_health and len(choices) == 1 and c.HELP_CHOICES.MONEY in choices)):
                choices.add(c.HELP_CHOICES.HEAL)

        return choices

    def get_help_choice(self):

        choices = [(choice, c.HELP_CHOICES_PRIORITY[choice]) for choice in self.help_choices]

        return random_value_by_priority(choices)

    @property
    def description_text_name(self):
        return '%s_description' % self.TEXTGEN_TYPE

    def get_info_link(self):
        return None

    def get_description(self):
        args = prepair_substitution(self.get_description_arguments())
        template = get_vocabulary().get_random_phrase(self.description_text_name)

        if template is None:
            raise Exception(self.description_text_name)

        msg = template.substitute(get_dictionary(), args)
        return msg

    def get_description_arguments(self):
        return {'hero': self.hero}

    def on_heal(self):
        pass

    #####################################
    # management
    #####################################
    def on_create(self):
        self.description = self.get_description()
        self.info_link = self.get_info_link()


    @classmethod
    def create(cls, hero, **kwargs):
        '''
        _storage argument used only in creating hero step
        '''

        bundle_id = None

        if hero.actions.has_actions:
            bundle_id = hero.actions.current_action.bundle_id

        _storage = None
        if '_storage' in kwargs:
            _storage = kwargs['_storage']
            del kwargs['_storage']

        if '_bundle_id' in kwargs:
            bundle_id = kwargs['_bundle_id']
            del kwargs['_bundle_id']

        action = cls._create(hero, bundle_id, **kwargs)

        if _storage:
            _storage.add_action(action)

        elif hero.actions.has_actions:
            hero.actions.current_action.storage.add_action(action)

        action.on_create()

        hero.actions.push_action(action)

        return action

    def remove(self, force=False):
        '''
        force - if True, storages will be ignored (need for full remove of angel & hero)
        '''

        if self.storage:
            self.storage.remove_action(self)

        self.hero.actions.pop_action()

        if self.quest:
            self.quest.remove()

        self.removed = True


    def on_save(self):
        if self.meta_action_id is not None and self.meta_action.updated:
            self.meta_action.save()

    def process_action(self):
        self.updated = True

        self.process()

        if not self.removed and self.state == self.STATE.PROCESSED:
            self.remove()


    def process_turn(self):
        self.process_action()

    def __eq__(self, other):

        return (self.removed == other.removed and
                self.TYPE == other.TYPE and
                self.percents == other.percents and
                self.state == other.state and
                self.hero.id == other.hero.id and
                self.context == other.context and
                self.mob_context == other.mob_context and
                self.place_id == other.place_id and
                self.mob == other.mob and
                self.quest_id == other.quest_id and
                self.data == other.data and
                self.break_at == other.break_at and
                self.length == other.length and
                self.destination_x == other.destination_x and
                self.destination_y == other.destination_y and
                self.percents_barier == other.percents_barier and
                self.extra_probability == other.extra_probability and
                self.textgen_id == other.textgen_id)




class ActionsContainer(object):

    __slots__ = ('updated', 'actions_list')

    def __init__(self):
        self.updated = False
        self.actions_list = []

    def serialize(self):
        return {'actions': [action.serialize() for action in self.actions_list]}

    @classmethod
    def deserialize(cls, hero, data):
        from game.actions.prototypes import ACTION_TYPES
        obj = cls()
        obj.actions_list = [ACTION_TYPES[action_data['type']].deserialize(hero=hero, data=action_data) for action_data in data.get('actions', [])]
        return obj

    def ui_info(self):
        return {'actions': [action.ui_info() for action in self.actions_list]}

    def push_action(self, action):
        self.updated = True
        self.actions_list.append(action)

    def pop_action(self):
        self.updated = True
        action = self.actions_list.pop()
        return action

    @property
    def current_action(self): return self.actions_list[-1]

    def on_save(self):
        for action in self.actions_list:
            action.on_save()

    @property
    def has_actions(self): return len(self.actions_list)

    @property
    def number(self): return len(self.actions_list)
