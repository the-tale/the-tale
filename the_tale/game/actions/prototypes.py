# coding: utf-8
# pylint: disable=C0302
import random
import copy
import math

from dext.common.utils.urls import url
from dext.common.utils import discovering

from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.prototypes import TimePrototype

from the_tale.game.heroes.relations import MONEY_SOURCE

from the_tale.game.balance import constants as c, formulas as f, enums as e

from the_tale.game.quests.logic import create_random_quest_for_hero

from the_tale.game.mobs.prototypes import MobPrototype
from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.map.roads.storage import waymarks_storage
from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.storage import map_info_storage

from the_tale.game.abilities.relations import HELP_CHOICES

from the_tale.game.actions import battle
from the_tale.game.actions import contexts
from the_tale.game.actions import exceptions
from the_tale.game.actions import relations



E = 0.0001


class ActionBase(object):

    __slots__ = ( 'hero',
                  'percents',
                  'bundle_id',
                  'description',
                  'state',
                  'removed',
                  'storage',
                  'created_at_turn',
                  'context',
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
                  'back',
                  'info_link',
                  'meta_action_id',
                  'replane_required')


    class STATE:
        UNINITIALIZED = 'uninitialized'
        PROCESSED = 'processed'

    TYPE = None
    SINGLE = True # is action work with only one hero
    TEXTGEN_TYPE = None
    CONTEXT_MANAGER = None
    HELP_CHOICES = set()
    APPROVED_FOR_STEPS_CHAIN = True
    HABIT_MODE = relations.ACTION_HABIT_MODE.PEACEFUL

    def __init__(self,
                 hero,
                 bundle_id,
                 state,
                 percents=0.0,
                 type=None, # just for deserialization
                 created_at_turn=None,
                 context=None,
                 description=None,
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
                 back=False,
                 info_link=None,
                 meta_action_id=None,
                 replane_required=False):

        self.updated = False

        self.hero = hero

        self.description = description

        self.percents = percents

        self.bundle_id = bundle_id

        self.state = state

        self.removed = False
        self.storage = None

        self.created_at_turn = created_at_turn if created_at_turn is not None else TimePrototype.get_current_turn_number()

        self.context = None
        self.mob_context = None

        if self.CONTEXT_MANAGER:
            self.context = context if context is None or isinstance(context, self.CONTEXT_MANAGER) else self.CONTEXT_MANAGER.deserialize(context)
            self.mob_context = mob_context if mob_context is None or isinstance(mob_context, self.CONTEXT_MANAGER) else self.CONTEXT_MANAGER.deserialize(mob_context)

        self.place_id = place_id

        self.mob = None
        if mob:
            self.mob = mob if isinstance(mob, MobPrototype) else MobPrototype.deserialize(mob)

        self.data = data
        self.break_at = break_at
        self.length = length
        self.destination_x = destination_x
        self.destination_y = destination_y
        self.percents_barier = percents_barier
        self.extra_probability = extra_probability
        self.textgen_id = textgen_id
        self.back = back
        self.meta_action_id = meta_action_id

        self.info_link = info_link

        self.replane_required = replane_required


    def serialize(self):
        data = {'type': self.TYPE.value,
                'bundle_id': self.bundle_id,
                'state': self.state,
                'percents': self.percents,
                'description': self.description,
                'created_at_turn': self.created_at_turn}
        if self.replane_required:
            data['replane_required'] = self.replane_required
        if self.context:
            data['context'] = self.context.serialize()
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
        if self.textgen_id is not None:
            data['textgen_id'] = self.textgen_id
        if self.back:
            data['back'] = self.back
        if self.meta_action_id is not None:
            data['meta_action_id'] = self.meta_action_id
        if self.info_link is not None:
            data['info_link'] = self.info_link

        return data

    @classmethod
    def deserialize(cls, hero, data):
        return cls(hero=hero, **data)

    @property
    def ui_type(self): return self.TYPE.value

    def ui_info(self):
        return {'percents': max(0.0, min(1.0, self.percents)),
                'type': self.ui_type,
                'description': self.description,
                'info_link': self.info_link,
                'is_boss': self.mob.is_boss if self.mob else None}

    @property
    def leader(self):
        return (not self.removed) and (self.hero.actions.current_action is self)

    def set_storage(self, storage):
        self.storage = storage

    @property
    def place(self): return places_storage[self.place_id]

    def get_destination(self): return self.destination_x, self.destination_y
    def set_destination(self, x, y):
        self.destination_x = x
        self.destination_y = y

    @property
    def meta_action(self):
        if self.storage is None: # if meta_action accessed from views (not from logic)
            return None
        return self.storage.meta_actions.get(self.meta_action_id) if self.meta_action_id else None

    @property
    def help_choices(self):
        choices = copy.copy(self.HELP_CHOICES)

        if HELP_CHOICES.HEAL in choices:
            if len(choices) > 1 and not self.hero.can_be_healed(strict=False):
                choices.remove(HELP_CHOICES.HEAL)
            elif not self.hero.can_be_healed(strict=True):
                choices.remove(HELP_CHOICES.HEAL)

        if HELP_CHOICES.HEAL_COMPANION in choices:
            if self.hero.companion is None:
                choices.remove(HELP_CHOICES.HEAL_COMPANION)
            elif self.hero.companion.health == self.hero.companion.max_health:
                choices.remove(HELP_CHOICES.HEAL_COMPANION)

        if HELP_CHOICES.STOCK_UP_ENERGY in choices:
            if self.hero.energy_bonus >= c.ANGEL_FREE_ENERGY_MAXIMUM:
                choices.remove(HELP_CHOICES.STOCK_UP_ENERGY)

        return choices

    def get_help_choice(self):

        choices = [(choice, choice.priority) for choice in self.help_choices]

        return random_value_by_priority(choices)

    @property
    def description_text_name(self):
        return '%s_description' % self.TEXTGEN_TYPE

    def get_info_link(self):
        return None

    def get_description(self):
        from the_tale.linguistics import logic as linguistics_logic
        return linguistics_logic.get_text(self.description_text_name, self.get_description_arguments())

    def get_description_arguments(self):
        return {'hero': self.hero}

    def on_heal(self):
        pass

    def on_heal_companion(self):
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

    def on_remove(self):
        pass

    def remove(self, force=False):
        '''
        force - if True, storages will be ignored (need for full remove of angel & hero)
        '''

        self.on_remove()

        if self.storage:
            self.storage.remove_action(self)

        self.hero.actions.pop_action()

        self.removed = True

    def on_save(self):

        if self.meta_action_id is not None and self.meta_action.updated:
            self.meta_action.save()

    def process_action(self):
        self.hero.actions.updated = True

        self.process()

        # remove only leader action
        # action can set PROCESSED state and create child action
        # is that case we should not remove action
        # it will be removed (by processing of chain actions in LogicStorage) when child action will be processed
        if self.leader and not self.removed and self.state == self.STATE.PROCESSED:
            self.remove()


    def process_turn(self):
        self.process_action()

    def choose_event_reward(self):
        return random_value_by_priority([(record, record.priority) for record in relations.ACTION_EVENT_REWARD.records])

    def do_events(self):

        habit_events = self.hero.habit_events()

        if not habit_events:
            return

        event = random.choice(list(habit_events))

        event_reward = self.choose_event_reward()

        message_type = 'action_event_habit_%s_%s_%s' % (self.TYPE.name.lower(), event.name.lower(), event_reward.name.lower())

        if event_reward.is_NOTHING:
            self.hero.add_message(message_type, diary=True, hero=self.hero, **self.action_event_message_arguments())
        elif event_reward.is_MONEY:
            multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
            coins = int(math.ceil(f.normal_loot_cost_at_lvl(self.hero.level) * multiplier))
            self.hero.change_money(MONEY_SOURCE.EARNED_FROM_HABITS, coins)
            self.hero.add_message(message_type, diary=True, hero=self.hero, coins=coins, **self.action_event_message_arguments())
        elif event_reward.is_ARTIFACT:
            artifact, unequipped, sell_price = self.hero.receive_artifact(equip=False, better=False, prefered_slot=False, prefered_item=False, archetype=False)
            self.hero.add_message(message_type, diary=True, hero=self.hero, artifact=artifact, **self.action_event_message_arguments())
        elif event_reward.is_EXPERIENCE:
            experience = self.hero.add_experience(int(c.HABIT_EVENT_EXPERIENCE * random.uniform(1.0-c.HABIT_EVENT_EXPERIENCE_DELTA, 1.0+c.HABIT_EVENT_EXPERIENCE_DELTA)))
            self.hero.add_message(message_type, diary=True, hero=self.hero, experience=experience, **self.action_event_message_arguments())

    def action_event_message_arguments(self):
        return {}


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
                self.data == other.data and
                self.break_at == other.break_at and
                self.length == other.length and
                self.destination_x == other.destination_x and
                self.destination_y == other.destination_y and
                self.percents_barier == other.percents_barier and
                self.extra_probability == other.extra_probability and
                self.textgen_id == other.textgen_id)



class ActionIdlenessPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.IDLENESS
    TEXTGEN_TYPE = 'action_idleness'

    @property
    def HELP_CHOICES(self): # pylint: disable=C0103
        choices = set((HELP_CHOICES.START_QUEST, HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

        if self.percents > 1.0 - E:
            choices.remove(HELP_CHOICES.START_QUEST)

        return choices

    class STATE(ActionBase.STATE):
        QUEST = 'QUEST'
        IN_PLACE = 'IN_PLACE'
        WAITING = 'WAITING'
        REGENERATE_ENERGY = 'regenerate_energy'
        RETURN = 'RETURN'
        RESURRECT = 'RESURRECT'

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

    def preprocess(self):
        if not self.hero.is_alive:
            ActionResurrectPrototype.create(hero=self.hero)
            self.state = self.STATE.RESURRECT
            return True

        return False

    def process_position(self):
        if self.hero.position.place is None:
            if self.hero.position.road:
                # choose nearest place in road
                if bool(self.hero.position.percents < 0.5) != self.hero.position.invert_direction:
                    destination = self.hero.position.road.point_1
                else:
                    destination = self.hero.position.road.point_2

                ActionMoveToPrototype.create(hero=self.hero, destination=destination)
            else:
                destination = self.hero.position.get_nearest_dominant_place()
                ActionMoveNearPlacePrototype.create(hero=self.hero, place=destination, back=True)

            self.state = self.STATE.RETURN
        else:
            self.state = self.STATE.IN_PLACE
            ActionInPlacePrototype.create(hero=self.hero)

        return self.state in (self.STATE.IN_PLACE, self.STATE.RETURN)

    def process(self):

        if self.preprocess():
            return

        if self.state == self.STATE.RESURRECT:
            if self.process_position():
                return
            self.state = self.STATE.WAITING

        if self.state == self.STATE.RETURN:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.IN_PLACE:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.REGENERATE_ENERGY:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.QUEST:
            self.percents = 0 # reset percents only when end quest
            if self.process_position():
                return
            self.state = self.STATE.WAITING

        if self.state == self.STATE.WAITING:

            if self.hero.position.place is None:
                self.process_position()
                return

            self.percents += 1.0 / self.hero.idle_length

            if self.percents >= 1.0:
                self.state = self.STATE.QUEST

                quest = create_random_quest_for_hero(self.hero)
                ActionQuestPrototype.create(hero=self.hero, quest=quest)

            elif self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
                ActionRegenerateEnergyPrototype.create(hero=self.hero)
                self.state = self.STATE.REGENERATE_ENERGY

            else:
                if random.uniform(0, 1) < 1.0 / c.TURNS_TO_IDLE / 2: # 1 фраза на два уровня героя
                    self.hero.add_message('action_idleness_waiting', hero=self.hero)


class ActionQuestPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.QUEST
    TEXTGEN_TYPE = 'action_quest'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))
    APPROVED_FOR_STEPS_CHAIN = False # all quest actions MUST be done on separated turns

    class STATE(ActionBase.STATE):
        PROCESSING = 'processing'

    ###########################################
    # Object operations
    ###########################################

    def on_create(self):
        super(ActionQuestPrototype, self).on_create()

    def on_remove(self):
        super(ActionQuestPrototype, self).on_remove()

    @classmethod
    def _create(cls, hero, bundle_id, quest):
        hero.quests.push_quest(quest)
        return cls(hero=hero,
                   bundle_id=bundle_id,
                   state=cls.STATE.PROCESSING)

    def process(self):

        if self.state == self.STATE.PROCESSING:

            if not self.hero.quests.has_quests:
                self.state = self.STATE.PROCESSED
                return

            percents = self.hero.quests.current_quest.process()

            self.percents = percents

            if self.hero.quests.current_quest.is_processed:
                self.hero.quests.pop_quest()
                self.state = self.STATE.PROCESSED


class ActionMoveToPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.MOVE_TO
    TEXTGEN_TYPE = 'action_moveto'
    SHORT_DESCRIPTION = u'путешествует'

    @property
    def HELP_CHOICES(self):
        choices = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

        if self.state == self.STATE.MOVING:
            choices.add(HELP_CHOICES.TELEPORT)

        return choices


    class STATE(ActionBase.STATE):
        CHOOSE_ROAD = 'choose_road'
        MOVING = 'moving'
        IN_CITY = 'in_city'
        BATTLE = 'battle'
        REGENERATE_ENERGY = 'regenerate_energy'
        RESTING = 'resting'
        RESURRECT = 'resurrect'
        HEALING_COMPANION = 'healing_companion'

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

    def teleport(self, distance, create_inplace_action):

        if self.state != self.STATE.MOVING:
            return False

        stop_percents = self.break_at if self.break_at else 1

        max_road_distance = self.hero.position.road.length * (1 - self.hero.position.percents)
        max_action_distance = self.length * (stop_percents - self.percents )

        distance = min(distance, min(max_road_distance, max_action_distance))

        self.hero.position.percents += distance / self.hero.position.road.length

        if self.length > E:
            self.percents += distance / self.length

        if self.hero.position.percents + E > 1:
            self.hero.position.percents = 1
            self.place_hero_in_current_destination(create_action=create_inplace_action)

        if self.percents + E > stop_percents:
            self.state = self.STATE.PROCESSED

        self.updated = True

        return True

    def teleport_to_place(self, create_inplace_action):

        if self.state != self.STATE.MOVING:
            return False

        return self.teleport(distance=self.hero.position.road.length+1, create_inplace_action=create_inplace_action)

    def teleport_to_end(self):
        if self.state != self.STATE.MOVING:
            return False

        while True:
            if not self.teleport_to_place(create_inplace_action=False):
                return False

            if self.state == self.STATE.PROCESSED:
                if self.hero.position.place:
                    ActionInPlacePrototype.create(hero=self.hero)
                return True

            self.process_choose_road()

    @property
    def current_destination(self): return self.hero.position.road.point_2 if not self.hero.position.invert_direction else self.hero.position.road.point_1

    def preprocess(self):
        if self.replane_required:
            self.state = self.STATE.PROCESSED
            return True

        if not self.hero.is_alive:
            ActionResurrectPrototype.create(hero=self.hero)
            self.state = self.STATE.RESURRECT
            return True

        if self.hero.need_rest_in_move:
            ActionRestPrototype.create(hero=self.hero)
            self.state = self.STATE.RESTING
            return True

        if self.hero.companion and self.hero.companion.need_heal_in_move:
            ActionHealCompanionPrototype.create(hero=self.hero)
            self.state = self.STATE.HEALING_COMPANION
            return True

        return False

    def process_choose_road__in_place(self):
        if self.hero.position.place_id != self.destination_id:
            waymark = waymarks_storage.look_for_road(point_from=self.hero.position.place_id, point_to=self.destination_id)
            length = waymark.length
            self.hero.position.set_road(waymark.road, invert=(self.hero.position.place_id != waymark.road.point_1_id))
            self.state = self.STATE.MOVING
        else:
            length = None
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
            length = length_right + delta_rigth

        percents = self.hero.position.percents
        if self.hero.position.invert_direction and not invert:
            percents = 1 - percents
        elif not self.hero.position.invert_direction and invert:
            percents = 1 - percents

        if length < 0.01:
            self.place_hero_in_current_destination()
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

        if self.hero.companion and random.random() < self.hero.companion_teleport_probability:
            self.hero.add_message('companions_teleport', companion_owner=self.hero, companion=self.hero.companion)
            self.teleport_to_place(create_inplace_action=True)
            return

    def normal_move(self):

        if self.hero.companion and self.hero.can_companion_say_wisdom() and random.random() < self.hero.companion_say_wisdom_probability:
            self.hero.add_experience(c.COMPANION_EXP_PER_MOVE_GET_EXP, without_modifications=True)
            self.hero.add_message('companions_say_wisdom', companion_owner=self.hero, companion=self.hero.companion, experience=c.COMPANION_EXP_PER_MOVE_GET_EXP)

        elif random.uniform(0, 1) < c.HABIT_MOVE_EVENTS_IN_TURN:
            self.do_events()

        elif random.uniform(0, 1) < 0.33:
            if self.destination.id != self.current_destination.id and random.uniform(0, 1) < 0.04: # TODO: change probability, when there are move phrases
                self.hero.add_message('action_moveto_move_long_path',
                                      hero=self.hero,
                                      destination=self.destination,
                                      current_destination=self.current_destination)
            else:
                self.hero.add_message('action_moveto_move',
                                      hero=self.hero,
                                      destination=self.destination,
                                      current_destination=self.current_destination)

        if self.hero.companion and random.random() < self.hero.companion_fly_probability:
            self.hero.add_message('companions_fly', companion_owner=self.hero, companion=self.hero.companion)
            self.teleport(c.ANGEL_HELP_TELEPORT_DISTANCE, create_inplace_action=True)
            return

        move_speed = self.hero.position.modify_move_speed(self.hero.move_speed)

        delta = move_speed / self.hero.position.road.length

        self.hero.position.percents += delta

        if self.length > 0.001:
            self.percents += move_speed / self.length
        else:
            self.percents = 1

    def picked_up_in_road(self):
        current_destination = self.current_destination # save destination befor telefort, since it can be reseted after we perfom it

        if self.teleport(c.PICKED_UP_IN_ROAD_TELEPORT_LENGTH, create_inplace_action=True):

            self.hero.add_message('action_moveto_picked_up_in_road',
                                hero=self.hero,
                                destination=self.destination,
                                current_destination=current_destination)



    def process_moving(self):

        if self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY

        elif self.hero.position.is_battle_start_needed():
            mob = mobs_storage.create_mob_for_hero(self.hero)
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
            self.state = self.STATE.BATTLE

        else:
            if self.hero.can_picked_up_in_road():
                self.picked_up_in_road()
            else:
                self.normal_move()

            if self.hero.position.percents >= 1:
                self.place_hero_in_current_destination()

            elif self.percents >= 1:
                self.state = self.STATE.PROCESSED

            elif self.break_at is not None and self.break_at < self.percents:
                self.state = self.STATE.PROCESSED

    def place_hero_in_current_destination(self, create_action=True):
        self.hero.position.percents = 1
        self.hero.position.set_place(self.current_destination)
        self.state = self.STATE.IN_CITY
        if create_action:
            ActionInPlacePrototype.create(hero=self.hero)

    def process(self):

        if self.preprocess():
            return

        if self.state in (self.STATE.RESTING, self.STATE.RESURRECT, self.STATE.REGENERATE_ENERGY, self.STATE.IN_CITY, self.STATE.HEALING_COMPANION):
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
                elif self.hero.companion and self.hero.companion.need_heal_in_move:
                    ActionHealCompanionPrototype.create(hero=self.hero)
                    self.state = self.STATE.HEALING_COMPANION
                else:
                    self.state = self.STATE.MOVING

        if self.state == self.STATE.CHOOSE_ROAD:
            self.process_choose_road()

        if self.state == self.STATE.MOVING:
            self.process_moving()


class ActionBattlePvE1x1Prototype(ActionBase):

    TYPE = relations.ACTION_TYPE.BATTLE_PVE_1X1
    TEXTGEN_TYPE = 'action_battlepve1x1'
    CONTEXT_MANAGER = contexts.BattleContext
    HABIT_MODE = relations.ACTION_HABIT_MODE.AGGRESSIVE

    @property
    def HELP_CHOICES(self): # pylint: disable=C0103
        if not self.hero.is_alive:
            return set((HELP_CHOICES.RESURRECT,))
        if self.mob.health <= 0:
            return set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))
        return set((HELP_CHOICES.LIGHTING, HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        BATTLE_RUNNING = 'battle_running'

    ###########################################
    # Object operations
    ###########################################

    def get_info_link(self):
        return url('guide:mobs:info', self.mob.record.id)

    @classmethod
    def _create(cls, hero, bundle_id, mob):

        kill_before_battle = hero.can_kill_before_battle()
        can_peacefull_battle = hero.can_peacefull_battle(mob.mob_type)
        can_leave_battle_in_fear = hero.can_leave_battle_in_fear()
        companions_is_exorcist = hero.companion and hero.can_companion_do_exorcism() and random.random() < hero.companion_do_exorcism_probability

        instant_kill_mob = False

        if kill_before_battle:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_kill_before_start', hero=hero, mob=mob)
            instant_kill_mob = True
        elif can_peacefull_battle:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_peacefull_battle', hero=hero, mob=mob)
        elif can_leave_battle_in_fear:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_leave_battle_in_fear', hero=hero, mob=mob)
        elif companions_is_exorcist and mob.mob_type.is_DEMON:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_companion_do_exorcims', hero=hero, mob=mob, companion=hero.companion)
            instant_kill_mob = True
        else:
            percents = 0.0
            state = cls.STATE.BATTLE_RUNNING
            hero.add_message('action_battlepve1x1_start', hero=hero, mob=mob)

        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         context=cls.CONTEXT_MANAGER(),
                         mob=mob,
                         mob_context=cls.CONTEXT_MANAGER(),
                         percents=percents,
                         state=state)

        if instant_kill_mob:
            prototype._kill_mob()

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

        if self.mob.health <= 0:
            self.on_mob_killed()

        self.updated = True

        return True

    def fast_resurrect(self):
        if self.state != self.STATE.PROCESSED: # hero can be dead only if action already processed
            return False

        if self.hero.is_alive:
            return False

        self.hero.resurrect()

        self.updated = True
        return True

    def _kill_mob(self):
        self.mob.kill()
        self.hero.statistics.change_pve_kills(1)

        loot = artifacts_storage.generate_loot(self.hero, self.mob)

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

        if self.hero.can_get_exp_for_kill():
            raw_experience = int(c.EXP_FOR_KILL*random.uniform(1.0-c.EXP_FOR_KILL_DELTA, 1.0+c.EXP_FOR_KILL_DELTA))
            real_experience = self.hero.add_experience(raw_experience)
            self.hero.add_message('action_battlepve1x1_exp_for_kill', hero=self.hero, mob=self.mob, diary=True, experience=real_experience)

        if (self.hero.companion and
            self.hero.companion.health < self.hero.companion.max_health and
            self.hero.can_companion_eat_corpses() and
            random.random() < self.hero.companion_eat_corpses_probability and
            self.mob.mob_type.is_eatable):
            self.hero.companion.health += c.COMPANIONS_HEAL_AMOUNT
            self.hero.add_message('companions_eat_corpse', companion_owner=self.hero, companion=self.hero.companion, health=c.COMPANIONS_HEAL_AMOUNT)


    def process_artifact_breaking(self):

        self.hero.damage_integrity()

        if random.uniform(0.0, 1.0) > c.ARTIFACTS_BREAKS_PER_BATTLE:
            return

        artifacts = self.hero.artifacts_to_break()

        if not len(artifacts):
            return

        artifact = random_value_by_priority([(artifact, 1 - artifact.integrity_fraction)
                                             for artifact in artifacts])

        artifact.break_it()
        self.hero.add_message('action_battlepve1x1_artifact_broken', hero=self.hero, mob=self.mob, diary=True, artifact=artifact)

    def on_mob_killed(self):
        self.hero.add_message('action_battlepve1x1_mob_killed', hero=self.hero, mob=self.mob)
        self._kill_mob()
        self.state = self.STATE.PROCESSED

    def on_hero_killed(self):
        self.hero.kill()
        self.hero.statistics.change_pve_deaths(1)
        self.hero.add_message('action_battlepve1x1_diary_hero_killed', diary=True, journal=False, hero=self.hero, mob=self.mob)
        self.hero.add_message('action_battlepve1x1_journal_hero_killed', hero=self.hero, mob=self.mob)
        self.state = self.STATE.PROCESSED

    def process(self):

        if self.state == self.STATE.BATTLE_RUNNING:

            # make turn only if mob still alive (it can be killed by angel)
            if self.mob.health > 0:
                battle.make_turn(battle.Actor(self.hero, self.context),
                                 battle.Actor(self.mob, self.mob_context),
                                 self.hero)
                self.percents = 1.0 - self.mob.health_percents

            if self.hero.health <= 0:
                self.on_hero_killed()

            if self.mob.health <= 0:
                self.on_mob_killed()

            if self.state == self.STATE.PROCESSED:
                self.process_artifact_breaking()


class ActionResurrectPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.RESURRECT
    TEXTGEN_TYPE = 'action_resurrect'
    HELP_CHOICES = set((HELP_CHOICES.RESURRECT,))

    class STATE(ActionBase.STATE):
        RESURRECT = 'resurrect'

    @classmethod
    def _create(cls, hero, bundle_id):
        hero.add_message('action_resurrect_start', hero=hero)

        return cls( hero=hero,
                    bundle_id=bundle_id,
                    state=cls.STATE.RESURRECT)

    def fast_resurrect(self):
        if self.state != self.STATE.RESURRECT:
            return False

        self.hero.actions.current_action.percents = self.percents

        self.hero.resurrect()
        self.state = self.STATE.PROCESSED

        self.updated = True
        return True


    def process(self):

        if self.state == self.STATE.RESURRECT:

            self.percents += 1.0 / self.hero.resurrect_length

            if random.uniform(0, 1) < 1.0 / c.TURNS_TO_RESURRECT / 2: # 1 фраза на два уровня героя
                self.hero.add_message('action_resurrect_resurrecting', hero=self.hero)

            if self.percents >= 1:
                self.hero.resurrect()
                self.state = self.STATE.PROCESSED
                self.hero.add_message('action_resurrect_finish', hero=self.hero)


class ActionInPlacePrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.IN_PLACE
    TEXTGEN_TYPE = 'action_inplace'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        SPEND_MONEY = 'spend_money'
        REGENERATE_ENERGY = 'regenerate_energy'
        CHOOSING = 'choosing'
        TRADING = 'trading'
        RESTING = 'resting'
        EQUIPPING = 'equipping'
        HEALING_COMPANION = 'healing_companion'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         state=cls.STATE.SPEND_MONEY)

        if hero.position.place.modifier:
            if hero.health < hero.max_health and hero.position.place.modifier.full_regen_allowed():
                hero.health = hero.max_health
                hero.add_message('action_inplace_instant_heal', hero=hero, place=hero.position.place)

            if hero.companion and hero.companion.health < hero.companion.max_health and hero.position.place.modifier.companion_regen_allowed():
                hero.companion.health += c.COMPANIONS_HEAL_AMOUNT
                hero.add_message('action_inplace_companion_heal', hero=hero, place=hero.position.place, companion=hero.companion)

        if (hero.energy < hero.energy_maximum and
            hero.position.place.modifier and hero.position.place.modifier.energy_regen_allowed() and
            hero.position.place != hero.position.previous_place):
            hero.change_energy(c.ANGEL_ENERGY_INSTANT_REGENERATION_IN_PLACE)
            hero.add_message('action_inplace_instant_energy_regen', hero=hero, place=hero.position.place)

        if (hero.position.place.tax > 0 and
            hero.position.place != hero.position.previous_place):

            if hero.money > 0:
                tax = int(hero.money * hero.position.place.tax)
                hero.change_money(MONEY_SOURCE.SPEND_FOR_TAX, -tax)
                hero.add_message('action_inplace_tax', hero=hero, place=hero.position.place, coins=tax, diary=True)
            else:
                hero.add_message('action_inplace_tax_no_money', hero=hero, place=hero.position.place, diary=True)

        if ( hero.position.place.can_habit_event() and
             hero.position.place != hero.position.previous_place ):

            if random.uniform(0, 1) < 0.5:
                hero.add_message('action_inplace_habit_event_honor_%s' % hero.position.place.habit_honor.interval.name.lower(),
                                 hero=hero, place=hero.position.place, diary=True)
            else:
                hero.add_message('action_inplace_habit_event_peacefulness_%s' % hero.position.place.habit_peacefulness.interval.name.lower(),
                                 hero=hero, place=hero.position.place, diary=True)
        if hero.companion and hero.position.place != hero.position.previous_place and hero.position.previous_place is not None:

            if hero.can_companion_eat():
                waymark = waymarks_storage.look_for_road(point_from=hero.position.previous_place.id, point_to=hero.position.place)
                coins = min(hero.money, int(math.ceil(f.gold_in_path(hero.level, waymark.length) * hero.companion_money_for_food_multiplier)+1))

                if coins > 0:
                    hero.change_money(MONEY_SOURCE.SPEND_FOR_COMPANIONS, -coins)
                    hero.add_message('action_inplace_companion_money_for_food', hero=hero, place=hero.position.place, companion=hero.companion, coins=coins)

            if not hero.bag.is_empty and hero.can_companion_drink_artifact() and random.random() < hero.companion_drink_artifact_probability:
                artifact = random.choice(hero.bag.values())
                hero.pop_loot(artifact)
                hero.add_message('action_inplace_companion_drink_artifact', hero=hero, place=hero.position.place, artifact=artifact, companion=hero.companion)

            if random.random() < hero.companion_leave_in_place_probability:
                hero.add_message('action_inplace_companion_leave', diary=True, hero=hero, place=hero.position.place, companion=hero.companion)
                hero.remove_companion()


        hero.position.visit_current_place()

        return prototype

    def action_event_message_arguments(self):
        return {'place': self.hero.position.place}

    def get_description_arguments(self):
        args = super(ActionInPlacePrototype, self).get_description_arguments()
        args.update({'place': self.hero.position.place})
        return args

    def process(self):
        return self.process_settlement()

    def try_to_spend_money(self):
        gold_amount = self.hero.spend_amount
        if gold_amount <= self.hero.money:
            gold_amount = min(self.hero.money, int(gold_amount * (1 + random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA))))
            gold_amount = self.hero.modify_buy_price(gold_amount)
            self.hero.change_money(self.hero.next_spending.money_source, -gold_amount)
            self.hero.switch_spending()
            return gold_amount

        return None

    def spend_money__instant_heal(self):
        if self.hero.health > self.hero.max_health * c.SPEND_MONEY_FOR_HEAL_HEALTH_FRACTION:
            return

        coins = self.try_to_spend_money()
        if coins is not None:
            self.hero.health = self.hero.max_health
            self.hero.add_message('action_inplace_diary_instant_heal_for_money', diary=True, hero=self.hero, coins=coins)

    def spend_money__buying_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:

            artifact, unequipped, sell_price = self.hero.receive_artifact(equip=True, better=True, prefered_slot=True, prefered_item=True, archetype=True)

            if unequipped is not None:
                if artifact.id == unequipped.id:
                    self.hero.add_message('action_inplace_diary_buying_artifact_and_change_equal_items', diary=True,
                                          hero=self.hero, artifact=artifact, coins=coins, sell_price=sell_price, coins_delta=coins-sell_price)
                else:
                    self.hero.add_message('action_inplace_diary_buying_artifact_and_change', diary=True,
                                          hero=self.hero, artifact=artifact, coins=coins, old_artifact=unequipped, sell_price=sell_price)
            else:
                self.hero.add_message('action_inplace_diary_buying_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__sharpening_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            artifact = self.hero.sharp_artifact()

            self.hero.add_message('action_inplace_diary_sharpening_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__repairing_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            artifact = self.hero.repair_artifact()

            self.hero.add_message('action_inplace_diary_repairing_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__useless(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            self.hero.add_message('action_inplace_diary_spend_useless', diary=True, hero=self.hero, coins=coins)

    def spend_money__impact(self):
        coins = self.try_to_spend_money()
        if coins is not None:

            choices = []

            if self.hero.preferences.friend is not None and self.hero.preferences.friend.place.id == self.hero.position.place.id:
                choices.append((True, self.hero.preferences.friend))

            if self.hero.preferences.enemy is not None and self.hero.preferences.enemy.place.id == self.hero.position.place.id:
                choices.append((False, self.hero.preferences.enemy))

            if not choices:
                choices.append((random.choice([True, False]), random.choice(self.hero.position.place.persons)))

            impact_type, person = random.choice(choices)

            if impact_type:
                power_direction = 1
                self.hero.add_message('action_inplace_diary_impact_good', diary=True, hero=self.hero, coins=coins, person=person)
            else:
                power_direction = -1
                self.hero.add_message('action_inplace_diary_impact_bad', diary=True, hero=self.hero, coins=coins, person=person)

            if not self.hero.can_change_person_power(person):
                return

            power, positive_bonus, negative_bonus = self.hero.modify_power(f.person_power_from_random_spend(power_direction, self.hero.level), person=person)
            person.cmd_change_power(power, positive_bonus, negative_bonus)

    def spend_money__experience(self):
        coins = self.try_to_spend_money()

        if coins is not None:
            experience = int(c.BASE_EXPERIENCE_FOR_MONEY_SPEND * (1.0 + random.uniform(-c.EXPERIENCE_DELTA_FOR_MONEY_SPEND, c.EXPERIENCE_DELTA_FOR_MONEY_SPEND)) + 1)
            self.hero.add_experience(experience)
            self.hero.add_message('action_inplace_diary_experience', diary=True, hero=self.hero, coins=coins, experience=experience)

    def spend_money(self):

        if self.hero.next_spending.is_INSTANT_HEAL:
            self.spend_money__instant_heal()

        elif self.hero.next_spending.is_BUYING_ARTIFACT:
            self.spend_money__buying_artifact()

        elif self.hero.next_spending.is_SHARPENING_ARTIFACT:
            self.spend_money__sharpening_artifact()

        elif self.hero.next_spending.is_REPAIRING_ARTIFACT:
            self.spend_money__repairing_artifact()

        elif self.hero.next_spending.is_USELESS:
            self.spend_money__useless()

        elif self.hero.next_spending.is_IMPACT:
            self.spend_money__impact()

        elif self.hero.next_spending.is_EXPERIENCE:
            self.spend_money__experience()

        else:
            raise exceptions.ActionException('wrong hero money spend type: %d' % self.hero.next_spending)


    def process_companion_stealing(self):

        if self.hero.companion is None:
            return

        if self.hero.can_companion_steal_money():
            money = int(f.normal_loot_cost_at_lvl(self.hero.level) * random.uniform(0.8, 1.2) * self.hero.companion_steal_money_modifier) + 1
            self.hero.change_money(MONEY_SOURCE.EARNED_FROM_COMPANIONS, money)
            self.hero.add_message('action_inplace_companion_steal_money', hero=self.hero, place=self.hero.position.place, companion=self.hero.companion, coins=money)

        if self.hero.can_companion_steal_item() and not self.hero.bag_is_full:
            loot = artifacts_storage.generate_any_artifact(self.hero, artifact_probability_multiplier=self.hero.companion_steal_artifact_probability_multiplier)

            self.hero.put_loot(loot)

            if loot.is_useless:
                self.hero.statistics.change_loot_had(1)
            else:
                self.hero.statistics.change_artifacts_had(1)

            self.hero.add_message('action_inplace_companion_steal_item', hero=self.hero, place=self.hero.position.place, artifact=loot, companion=self.hero.companion)


    def process_settlement(self):

        if self.state == self.STATE.SPEND_MONEY:
            self.state = self.STATE.CHOOSING
            self.spend_money()

        if self.state in [self.STATE.RESTING, self.STATE.HEALING_COMPANION, self.STATE.EQUIPPING, self.STATE.TRADING, self.STATE.REGENERATE_ENERGY]:
            self.state = self.STATE.CHOOSING

        if self.state == self.STATE.CHOOSING:

            if random.uniform(0, 1) < c.HABIT_IN_PLACE_EVENTS_IN_TURN:
                self.do_events()

            if self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
                self.state = self.STATE.REGENERATE_ENERGY
                ActionRegenerateEnergyPrototype.create(hero=self.hero)

            elif self.hero.need_rest_in_settlement:
                self.state = self.STATE.RESTING
                ActionRestPrototype.create(hero=self.hero)

            elif self.hero.companion and self.hero.companion.need_heal_in_settlement:
                self.state = self.STATE.HEALING_COMPANION
                ActionHealCompanionPrototype.create(hero=self.hero)

            elif self.hero.need_equipping_in_town:
                self.state = self.STATE.EQUIPPING
                ActionEquippingPrototype.create(hero=self.hero)

            elif self.hero.need_trade_in_town:
                self.state = self.STATE.TRADING
                ActionTradingPrototype.create(hero=self.hero)

            else:
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.process_companion_stealing()


class ActionRestPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.REST
    TEXTGEN_TYPE = 'action_rest'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

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

        if self.hero.health >= self.hero.max_health:
            self.state = self.STATE.PROCESSED

    def process(self):

        if self.hero.health >= self.hero.max_health:
            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.RESTING:

            heal_amount = int(round(float(self.hero.max_health) / self.hero.rest_length * (1 + random.uniform(-c.HEAL_STEP_FRACTION, c.HEAL_STEP_FRACTION))))

            heal_amount = self.hero.heal(heal_amount)

            if random.uniform(0, 1) < 0.2:
                self.hero.add_message('action_rest_resring', hero=self.hero, health=heal_amount)

            self.percents = float(self.hero.health)/self.hero.max_health

            if self.hero.health >= self.hero.max_health:
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.hero.health = self.hero.max_health




class ActionEquippingPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.EQUIPPING
    TEXTGEN_TYPE = 'action_equipping'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

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

            slot, unequipped, equipped = self.hero.equip_from_bag()

            if equipped:
                if unequipped:
                    if equipped.id == unequipped.id:
                        self.hero.add_message('action_equipping_diary_change_equal_items', diary=True, hero=self.hero, item=equipped)
                    else:
                        self.hero.add_message('action_equipping_diary_change_item', diary=True, hero=self.hero, unequipped=unequipped, equipped=equipped)
                else:
                    self.hero.add_message('action_equipping_diary_equip_item', diary=True, hero=self.hero, equipped=equipped)
            else:
                self.state = self.STATE.PROCESSED


class ActionTradingPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.TRADING
    TEXTGEN_TYPE = 'action_trading'
    SHORT_DESCRIPTION = u'торгует'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        TRADING = 'trading'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         percents_barier=hero.bag.occupation,
                         state=cls.STATE.TRADING)
        hero.add_message('action_trading_start', hero=hero)
        return prototype

    def process(self):

        if self.replane_required:
            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.TRADING:

            if not self.hero.bag.is_empty:
                artifact = random.choice(self.hero.bag.values())
                sell_price = self.hero.sell_artifact(artifact)
                self.hero.add_message('action_trading_sell_item', hero=self.hero, artifact=artifact, coins=sell_price)

            loot_items_count = self.hero.bag.occupation # pylint: disable=W0612

            if loot_items_count:
                self.percents = 1 - float(loot_items_count - 1) / self.percents_barier
            else:
                self.state = self.STATE.PROCESSED


class ActionMoveNearPlacePrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.MOVE_NEAR_PLACE
    TEXTGEN_TYPE = 'action_movenearplace'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        MOVING = 'MOVING'
        BATTLE = 'BATTLE'
        REGENERATE_ENERGY = 'REGENERATE_ENERGY'
        RESTING = 'RESTING'
        RESURRECT = 'RESURRECT'
        IN_CITY = 'IN_CITY'
        HEALING_COMPANION = 'healing_companion'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _get_destination_coordinates(cls, back, place, terrains):
        if back:
            return place.x, place.y
        else:
            choices = ()

            if terrains is not None:
                map_info = map_info_storage.item
                choices = [ (x, y) for x, y in place.nearest_cells if map_info.terrain[y][x] in terrains]

            if not choices:
                choices = place.nearest_cells

            return random.choice(choices)

    @classmethod
    def _create(cls, hero, bundle_id, place, back, terrains=None):

        x, y = cls._get_destination_coordinates(back=back, place=place, terrains=terrains)

        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         place_id=place.id,
                         destination_x=x,
                         destination_y=y,
                         state=cls.STATE.MOVING,
                         back=back)

        from_x, from_y = hero.position.cell_coordinates

        hero.position.set_coordinates(from_x, from_y, x, y, percents=0)

        return prototype

    def get_description_arguments(self):
        args = super(ActionMoveNearPlacePrototype, self).get_description_arguments()
        args.update({'place': self.place})
        return args


    def preprocess(self):

        if self.replane_required:
            self.state = self.STATE.PROCESSED
            return True

        if not self.hero.is_alive:
            ActionResurrectPrototype.create(hero=self.hero)
            self.state = self.STATE.RESURRECT
            return True

        if self.hero.need_rest_in_move:
            ActionRestPrototype.create(hero=self.hero)
            self.state = self.STATE.RESTING
            return True

        if self.hero.companion and self.hero.companion.need_heal_in_move:
            ActionHealCompanionPrototype.create(hero=self.hero)
            self.state = self.STATE.HEALING_COMPANION
            return True

        return False

    def process_battle(self):

        if self.hero.need_regenerate_energy:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY
            return

        if self.hero.need_rest_in_move:
            ActionRestPrototype.create(hero=self.hero)
            self.state = self.STATE.RESTING
            return

        self.state = self.STATE.MOVING


    def process_moving(self):


        if self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY

        elif self.hero.position.is_battle_start_needed():
            mob = mobs_storage.create_mob_for_hero(self.hero)
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
            self.state = self.STATE.BATTLE

        else:

            if self.hero.companion and self.hero.can_companion_say_wisdom() and random.random() < c.COMPANION_EXP_PER_MOVE_PROBABILITY:
                self.hero.add_experience(c.COMPANION_EXP_PER_MOVE_GET_EXP, without_modifications=True)
                self.hero.add_message('companions_say_wisdom', companion_owner=self.hero, companion=self.hero.companion, experience=c.COMPANION_EXP_PER_MOVE_GET_EXP)

            elif random.uniform(0, 1) < 0.25:
                self.hero.add_message('action_movenearplace_walk', hero=self.hero, place=self.place)


            if self.hero.position.subroad_len() == 0:
                self.hero.position.percents += 0.1
            else:
                move_speed = self.hero.position.modify_move_speed(self.hero.move_speed)
                delta = move_speed / self.hero.position.subroad_len()
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

        if self.preprocess():
            return

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

    TYPE = relations.ACTION_TYPE.REGENERATE_ENERGY
    TEXTGEN_TYPE = 'action_regenerate_energy'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

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
                multiplier = 2 if self.hero.can_regenerate_double_energy else 1
                energy_delta = self.hero.change_energy(f.angel_energy_regeneration_amount(self.regeneration_type)*multiplier)
                self.hero.last_energy_regeneration_at_turn = TimePrototype.get_current_turn_number()

                if energy_delta:
                    self.hero.add_message('action_regenerate_energy_energy_received_%s' % self.regeneration_slug(self.regeneration_type), hero=self.hero, energy=energy_delta)
                else:
                    self.hero.add_message('action_regenerate_energy_no_energy_received_%s' % self.regeneration_slug(self.regeneration_type), hero=self.hero)

                self.state = self.STATE.PROCESSED


class ActionDoNothingPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.DO_NOTHING
    TEXTGEN_TYPE = 'no texgen type'
    SHORT_DESCRIPTION = u'торгует'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))

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

    SINGLE = False
    TYPE = relations.ACTION_TYPE.META_PROXY
    TEXTGEN_TYPE = 'no texgen type'
    SHORT_DESCRIPTION = u'no description'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.HEAL_COMPANION))
    APPROVED_FOR_STEPS_CHAIN = False

    @property
    def description_text_name(self):
        return self.meta_action.description_text_name

    @property
    def ui_type(self):
        if self.meta_action is None:
            return self.TYPE.value
        return self.meta_action.TYPE.value

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


class ActionHealCompanionPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.HEAL_COMPANION
    TEXTGEN_TYPE = 'action_heal_companion'
    HELP_CHOICES = set((HELP_CHOICES.HEAL_COMPANION, ))

    HABIT_MODE = relations.ACTION_HABIT_MODE.COMPANION

    class STATE(ActionBase.STATE):
        HEALING = 'healing'

    def get_description_arguments(self):
        args = super(ActionHealCompanionPrototype, self).get_description_arguments()
        if self.hero.companion:
            args.update({'companion': self.hero.companion})
        return args

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls( hero=hero,
                         bundle_id=bundle_id,
                         state=cls.STATE.HEALING)
        hero.companion.on_heal_started()
        hero.add_message('action_heal_companion_start', hero=hero, companion=hero.companion)
        return prototype

    def after_processed(self):
        if self.hero.companion is None:
            return

        if self.hero.can_companion_exp_per_heal() and random.random() < self.hero.companion_exp_per_heal_probability:
            self.hero.add_experience(c.COMPANION_EXP_PER_HEAL, without_modifications=True)

        if (self.hero.companion.health < self.hero.companion.max_health and
            self.hero.can_companion_regenerate() and
            random.random() < self.hero.companion_regenerate_probability):
            self.hero.companion.health += c.COMPANIONS_HEAL_AMOUNT
            self.hero.add_message('companions_regenerate', companion_owner=self.hero, companion=self.hero.companion, health=c.COMPANIONS_HEAL_AMOUNT)

        if (self.hero.companion.health < self.hero.companion.max_health and
            ( (self.hero.companion.type.is_LIVING and random.random() < self.hero.companion_living_heal_probability) or
              (self.hero.companion.type.is_CONSTRUCT and random.random() < self.hero.companion_construct_heal_probability) or
              (self.hero.companion.type.is_UNUSUAL and random.random() < self.hero.companion_unusual_heal_probability) )
              ):
            self.hero.companion.health += c.COMPANIONS_HEAL_AMOUNT
            self.hero.add_message('hero_ability_companion_healing', hero=self.hero, companion=self.hero.companion, health=c.COMPANIONS_HEAL_AMOUNT)


    def on_heal_companion(self):
        if self.hero.companion is None:
            self.state = self.STATE.PROCESSED
            return

        if self.hero.companion.health >= self.hero.companion.max_health:
            self.state = self.STATE.PROCESSED

        heal_length = f.companions_heal_length(self.hero.companion.health, self.hero.companion.max_health)

        self.percents += float(c.COMPANIONS_HEAL_AMOUNT) / heal_length

        if self.percents >= 1.0 or self.hero.companion.health == self.hero.companion.max_health:
            self.percents = 1
            self.state = self.STATE.PROCESSED

    def process(self):

        if self.hero.companion is None:
            self.state = self.STATE.PROCESSED
            return

        if self.hero.companion.health >= self.hero.companion.max_health:
            self.hero.companion.health = self.hero.companion.max_health
            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.HEALING:

            heal_length = f.companions_heal_length(self.hero.companion.health, self.hero.companion.max_health)

            self.percents += 1.0 / heal_length

            if random.uniform(0, 1) < 0.1:
                self.hero.add_message('action_heal_companion_healing', hero=self.hero, companion=self.hero.companion)

            if self.percents >= 1.0:
                self.percents = 1
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.after_processed()





ACTION_TYPES = { action_class.TYPE:action_class
                 for action_class in discovering.discover_classes(globals().values(), ActionBase) }
