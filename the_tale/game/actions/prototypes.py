# coding: utf-8
# pylint: disable=C0302
import random
import copy

from dext.utils.urls import url

from common.utils.discovering import discover_classes
from common.utils.decorators import lazy_property
from common.utils.logic import random_value_by_priority

from game.heroes.logic import create_mob_for_hero

from game.map.roads.storage import waymarks_storage

from game.actions import battle, contexts

from game.balance import constants as c, formulas as f, enums as e

from game.actions.exceptions import ActionException

from game.quests.logic import create_random_quest_for_hero

from game.mobs.prototypes import MobPrototype

from game.prototypes import TimePrototype

from game.map.places.storage import places_storage

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

from game.abilities.relations import HELP_CHOICES


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
                  'info_link',
                  'meta_action_id')


    class STATE:
        UNINITIALIZED = 'uninitialized'
        PROCESSED = 'processed'

    TYPE = 'BASE'
    TEXTGEN_TYPE = None
    CONTEXT_MANAGER = None
    HELP_CHOICES = set()

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
                 info_link=None,
                 meta_action_id=None):

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

        self.quest_id = quest_id
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
        self.hero_health_lost = hero_health_lost
        self.back = back
        self.meta_action_id = meta_action_id

        self.info_link = info_link


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
        if self.textgen_id is not None:
            data['textgen_id'] = self.textgen_id
        if self.hero_health_lost != 0:
            data['hero_health_lost'] = self.hero_health_lost
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

    def ui_info(self):
        return {'percents': self.percents,
                'description': self.description,
                'info_link': self.info_link}

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
        choices = copy.copy(self.HELP_CHOICES)

        if HELP_CHOICES.HEAL in choices:
            if len(choices) > 1 and not self.hero.can_be_healed(strict=False):
                choices.remove(HELP_CHOICES.HEAL)
            elif not self.hero.can_be_healed(strict=True):
                choices.remove(HELP_CHOICES.HEAL)

        if HELP_CHOICES.STOCK_UP_ENERGY in choices:
            if self.hero.energy_charges >= c.ANGEL_FREE_ENERGY_CHARGES_MAXIMUM:
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

        if self.quest:
            self.quest.remove()

        self.removed = True

    def on_save(self):

        if self.meta_action_id is not None and self.meta_action.updated:
            self.meta_action.save()

    def process_action(self):
        self.hero.actions.updated = True

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



class ActionIdlenessPrototype(ActionBase):

    TYPE = 'IDLENESS'
    TEXTGEN_TYPE = 'action_idleness'

    @property
    def HELP_CHOICES(self): # pylint: disable=C0103
        choices = set((HELP_CHOICES.START_QUEST, HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

        if self.percents > 1.0 - E:
            choices.remove(HELP_CHOICES.START_QUEST)

        return choices

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

            self.percents += 1.0 / (c.TURNS_TO_IDLE * self.hero.level)

            if self.percents >= 1.0:
                self.state = self.STATE.QUEST

                quest = create_random_quest_for_hero(self.hero)
                ActionQuestPrototype.create(hero=self.hero, quest=quest)
                self.percents = 0

            elif self.hero.need_regenerate_energy and self.hero.preferences.energy_regeneration_type != e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE:
                ActionRegenerateEnergyPrototype.create(hero=self.hero)
                self.state = self.STATE.REGENERATE_ENERGY

            else:
                if random.uniform(0, 1) < 1.0 / c.TURNS_TO_IDLE / 2: # 1 фраза на два уровня героя
                    self.hero.add_message('action_idleness_waiting', hero=self.hero)


class ActionQuestPrototype(ActionBase):

    TYPE = 'QUEST'
    TEXTGEN_TYPE = 'action_quest'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

    class STATE(ActionBase.STATE):
        PROCESSING = 'processing'

    ###########################################
    # Object operations
    ###########################################

    def on_create(self):
        super(ActionQuestPrototype, self).on_create()
        self.hero.force_save_required = True

    def on_remove(self):
        super(ActionQuestPrototype, self).on_remove()
        self.hero.force_save_required = True

    @classmethod
    def _create(cls, hero, bundle_id, quest):
        return cls(hero=hero,
                   bundle_id=bundle_id,
                   quest_id=quest.id,
                   state=cls.STATE.PROCESSING)

    def process(self):
        if self.state == self.STATE.PROCESSING:
            percents = self.quest.process(self)
            self.quest.save()

            self.percents = percents

            if self.percents >= 1:
                self.percents = 1
                self.state = self.STATE.PROCESSED


class ActionMoveToPrototype(ActionBase):

    TYPE = 'MOVE_TO'
    TEXTGEN_TYPE = 'action_moveto'
    SHORT_DESCRIPTION = u'путешествует'
    HELP_CHOICES = set((HELP_CHOICES.TELEPORT, HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
                if random.uniform(0, 1) < 0.04: # TODO: change probability, when there are move phrases
                    self.hero.add_message('action_moveto_move_long_path',
                                          hero=self.hero,
                                          destination=self.destination,
                                          current_destination=self.current_destination)
                else:
                    self.hero.add_message('action_moveto_move',
                                          hero=self.hero,
                                          destination=self.destination,
                                          current_destination=self.current_destination)

            move_speed = self.hero.position.modify_move_speed(self.hero.move_speed)

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
    def HELP_CHOICES(self): # pylint: disable=C0103
        if self.mob.health <= 0:
            return set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))
        return set((HELP_CHOICES.LIGHTING, HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
                self.hero.add_message('action_battlepve1x1_diary_hero_killed', diary=True, journal=False, hero=self.hero, mob=self.mob)
                self.hero.add_message('action_battlepve1x1_journal_hero_killed', hero=self.hero, mob=self.mob)
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
    HELP_CHOICES = set((HELP_CHOICES.RESURRECT,))

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

            self.percents += 1.0 / (c.TURNS_TO_RESURRECT * self.hero.level)

            if random.uniform(0, 1) < 1.0 / c.TURNS_TO_RESURRECT / 2: # 1 фраза на два уровня героя
                self.hero.add_message('action_resurrect_resurrecting', hero=self.hero)

            if self.percents >= 1:
                self.percents = 1
                self.hero.resurrect()
                self.state = self.STATE.PROCESSED
                self.hero.add_message('action_resurrect_finish', hero=self.hero)


class ActionInPlacePrototype(ActionBase):

    TYPE = 'IN_PLACE'
    TEXTGEN_TYPE = 'action_inplace'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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

    @staticmethod
    def get_spend_amount(level, spending):
        return f.normal_action_price(level) * spending.price_fraction

    def try_to_spend_money(self):
        gold_amount = self.get_spend_amount(self.hero.level, self.hero.next_spending)
        if gold_amount <= self.hero.money:
            gold_amount = min(self.hero.money, int(gold_amount * (1 + random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA))))
            gold_amount = self.hero.modify_buy_price(gold_amount)
            self.hero.change_money(self.hero.next_spending.money_source, -gold_amount)
            self.hero.switch_spending()
            return gold_amount

        return None

    def spend_money__instant_heal(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            self.hero.health = self.hero.max_health
            self.hero.add_message('action_inplace_diary_instant_heal_for_money', diary=True, hero=self.hero, coins=coins)

    def spend_money__buying_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:

            better = self.hero.can_buy_better_artifact()

            artifact, unequipped, sell_price = self.hero.buy_artifact(better=better, with_preferences=False)

            if unequipped is not None:
                self.hero.add_message('action_inplace_diary_buying_artifact_and_change', diary=True,
                                      hero=self.hero, artifact=artifact, coins=coins, old_artifact=unequipped, sell_price=sell_price)
            else:
                self.hero.add_message('action_inplace_diary_buying_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__sharpening_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            artifact = self.hero.sharp_artifact()

            self.hero.add_message('action_inplace_diary_sharpening_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__useless(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            self.hero.add_message('action_inplace_diary_spend_useless', diary=True, hero=self.hero, coins=coins)

    def spend_money__impact(self):
        coins = self.try_to_spend_money()
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
                self.hero.add_message('action_inplace_diary_impact_good', diary=True, hero=self.hero, coins=coins, person=person)
            else:
                person.cmd_change_power(f.person_power_from_random_spend(-1, self.hero.level))
                self.hero.add_message('action_inplace_diary_impact_bad', diary=True, hero=self.hero, coins=coins, person=person)

    def spend_money__experience(self):
        coins = self.try_to_spend_money()

        if coins is not None:
            experience = int(c.BASE_EXPERIENCE_FOR_MONEY_SPEND * (1.0 + random.uniform(-c.EXPERIENCE_DELTA_FOR_MONEY_SPEND, c.EXPERIENCE_DELTA_FOR_MONEY_SPEND)) + 1)
            self.hero.add_experience(experience)
            self.hero.add_message('action_inplace_diary_experience', diary=True, hero=self.hero, coins=coins, experience=experience)

    def spend_money(self):

        if self.hero.next_spending._is_INSTANT_HEAL:
            self.spend_money__instant_heal()

        elif self.hero.next_spending._is_BUYING_ARTIFACT:
            self.spend_money__buying_artifact()

        elif self.hero.next_spending._is_SHARPENING_ARTIFACT:
            self.spend_money__sharpening_artifact()

        elif self.hero.next_spending._is_USELESS:
            self.spend_money__useless()

        elif self.hero.next_spending._is_IMPACT:
            self.spend_money__impact()

        elif self.hero.next_spending._is_EXPERIENCE:
            self.spend_money__experience()

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
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
                        self.hero.add_message('action_equipping_diary_change_equal_items', diary=True, hero=self.hero, item=equipped)
                    else:
                        self.hero.add_message('action_equipping_diary_change_item', diary=True, hero=self.hero, unequipped=unequipped, equipped=equipped)
                else:
                    self.hero.add_message('action_equipping_diary_equip_item', diary=True, hero=self.hero, equipped=equipped)
            else:
                self.state = self.STATE.PROCESSED


class ActionTradingPrototype(ActionBase):

    TYPE = 'TRADING'
    TEXTGEN_TYPE = 'action_trading'
    SHORT_DESCRIPTION = u'торгует'
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
    HELP_CHOICES = set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY, HELP_CHOICES.EXPERIENCE, HELP_CHOICES.STOCK_UP_ENERGY))

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
