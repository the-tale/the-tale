# -*- coding: utf-8 -*-
import copy
import random

from dext.utils import s11n
from dext.utils import database

from game.heroes.logic import create_mob_for_hero
from game.heroes.bag import SLOTS_LIST
from game.heroes.statistics import MONEY_SOURCE

from game.map.places.storage import places_storage
from game.map.roads.prototypes import get_road_by_model, WaymarkPrototype

from game.mobs.storage import MobsDatabase

from game.actions.models import Action, UNINITIALIZED_STATE
from game.actions import battle, contexts

from game.balance import constants as c, formulas as f
from game.game_info import ITEMS_OF_EXPENDITURE

from game.artifacts.storage import ArtifactsDatabase
from game.artifacts.conf import RARITY_TYPE

from game.actions.exceptions import ActionException

from game.quests.logic import create_random_quest_for_hero

from game.workers.environment import workers_environment

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution
from game.prototypes import TimePrototype


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


class HELP_CHOICES:
    HEAL = 0
    TELEPORT = 1
    LIGHTING = 2
    START_QUEST = 3
    MONEY = 4
    RESURRECT = 5


class ActionPrototype(object):

    TYPE = 'BASE'
    TEXTGEN_TYPE = None
    CONTEXT_MANAGER = None
    EXTRA_HELP_CHOICES = set()

    class STATE:
        UNINITIALIZED = UNINITIALIZED_STATE
        PROCESSED = 'processed'

    def __init__(self, model, *argv, **kwargs):
        super(ActionPrototype, self).__init__(*argv, **kwargs)
        self.model = model
        self.removed = False
        self.bundle = None
        self.updated = False

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

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def hero(self):
        return self.bundle.heroes[self.hero_id]

    @property
    def parent(self):
        if self.model.parent_id is not None:
            return self.bundle.actions[self.model.parent_id]
        return None

    @property
    def context(self):
        if not hasattr(self, '_context'):
            self._context = None
            if self.CONTEXT_MANAGER is not  None:
                self._context = self.CONTEXT_MANAGER.deserialize(s11n.from_json(self.model.context))
        return self._context

    @property
    def mob_context(self):
        if not hasattr(self, '_mob_context'):
            self._mob_context = None
            if self.CONTEXT_MANAGER is not  None:
                self._mob_context = self.CONTEXT_MANAGER.deserialize(s11n.from_json(self.model.mob_context))
        return self._mob_context

    @property
    def road_id(self): return self.model.road_id

    @property
    def place_id(self): return self.model.place_id

    @property
    def place(self): return places_storage[self.model.place_id]

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
        from ..mobs.prototypes import MobPrototype
        if not hasattr(self, '_mob'):
            mob_data = s11n.from_json(self.model.mob)
            self._mob = None
            if mob_data:
                self._mob = MobPrototype.deserialize(MobsDatabase.storage(), mob_data)
        return self._mob

    def remove_mob(self):
        delattr(self, '_mob')
        self.model.mob = '{}'

    @property
    def quest(self):
        from game.quests.prototypes import get_quest_by_model
        if not hasattr(self, '_quest'):
            self._quest = None
            if self.model.quest:
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

    def get_percents_barier(self): return self.model.percents_barier
    def set_percents_barier(self, value): self.model.percents_barier = value
    percents_barier = property(get_percents_barier, set_percents_barier)

    def get_help_choice(self):
        choices = copy.copy(self.EXTRA_HELP_CHOICES)
        choices.add(HELP_CHOICES.MONEY)

        if c.ANGEL_HELP_HEAL_IF_LOWER_THEN * self.hero.max_health > self.hero.health:
            choices.add(HELP_CHOICES.HEAL)

        return random.choice(list(choices))

    def get_description(self):
        template_name = '%s_description' % self.TEXTGEN_TYPE
        args = prepair_substitution(self.get_description_arguments())
        template = get_vocabulary().get_random_phrase(template_name)

        # from django.utils.log import getLogger
        # logger=getLogger('the-tale.workers.game_logic')
        # logger.error(template_name)

        if template is None:
            raise Exception(template_name)
            # TODO: raise exception in production (not when tests running)
            # from textgen.exceptions import TextgenException
            # raise TextgenException(u'ERROR: unknown template type: %s' % type_)
            return
        msg = template.substitute(get_dictionary(), args)
        return msg

    def get_description_arguments(self):
        return {'hero': self.hero}

    ###########################################
    # Object operations
    ###########################################

    def on_create(self, parent):
        if parent:
            parent.updated = True
            parent.leader = False
            parent.bundle.add_action(self)
        self.hero.push_action_description(self.get_description())
        self.hero.last_action_percents = self.percents

    def on_remove(self, force=False):
        if force:
            return

        if self.parent:
            self.parent.leader = True
            self.hero.last_action_percents = self.parent.percents
        else:
            self.hero.last_action_percents = 0

        self.hero.pop_action_description()

    @classmethod
    def create(cls, parent, *argv, **kwargs):
        '''
        _bundle argument used only in creating hero step
        '''
        _bundle = None
        if '_bundle' in kwargs:
            _bundle = kwargs['_bundle']
            del kwargs['_bundle']

        action = cls._create(parent, *argv, **kwargs)

        if _bundle:
            _bundle.add_action(action)

        action.on_create(parent)
        return action

    def remove(self, force=False):
        '''
        force - if True, bundles will be ignored (need for full remove of angel & hero)
        '''
        self.on_remove(force=force)

        if self.bundle:
            self.bundle.remove_action(self)

        if self.quest:
            self.quest.remove()

        self.model.delete()
        self.removed = True

    def save(self):
        if hasattr(self, '_data'):
            self.model.data = s11n.to_json(self._data)
        if hasattr(self, '_mob'):
            self.model.mob = s11n.to_json(self.mob.serialize()) if self.mob else '{}'
        if self.context:
            self.model.context = s11n.to_json(self.context.serialize())
        if self.mob_context:
            self.model.mob_context = s11n.to_json(self.mob_context.serialize())
        if hasattr(self, '_quest'):
            self._quest.save()

        database.raw_save(self.model)
        # self.model.save(force_update=True)

        self.updated = False

    def ui_info(self):

        return {'id': self.id,
                'type': self.type,
                'description': 'bla-bla-bla',
                'percents': self.percents,
                'specific': {'place_id': self.place_id,
                             'road_id': self.road_id,
                             'mob': self.mob.ui_info() if self.mob else None},
                'data': self.data #TODO: get json directly from self.model.data, without reloading it
                }

    def process_action(self):

        self.updated = True

        self.process()

        if self.leader:
            self.hero.last_action_percents = self.percents

        if not self.removed:

            if self.state == self.STATE.PROCESSED:
                self.remove()


    def process_turn(self):
        self.process_action()
        return TimePrototype.get_current_turn_number() + 1


    def __eq__(self, other):
        # print 'action'
        # print self.id == other.id
        # print self.removed == other.removed
        # print self.type == other.type
        # print self.order == other.order
        # print self.leader == other.leader
        # print self.percents == other.percents
        # print self.state == other.state
        # print self.hero_id == other.hero_id
        # print self.context == other.context
        # print self.mob_context == other.mob_context
        # print self.road_id == other.road_id
        # print self.place_id == other.place_id
        # print self.mob == other.mob
        # print self.model.quest_id == other.model.quest_id
        # print self.data == other.data
        # print self.break_at == other.break_at
        # print self.length == other.length
        # print self.get_destination() == other.get_destination()
        # print self.percents_barier == other.percents_barier
        return (self.id == other.id and
                self.removed == other.removed and
                self.type == other.type and
                self.order == other.order and
                self.leader == other.leader and
                self.percents == other.percents and
                self.state == other.state and
                self.hero_id == other.hero_id and
                self.context == other.context and
                self.mob_context == other.mob_context and
                self.road_id == other.road_id and
                self.place_id == other.place_id and
                self.mob == other.mob and
                self.model.quest_id == other.model.quest_id and # TODO: is that needed
                self.data == other.data and
                self.break_at == other.break_at and
                self.length == other.length and
                self.get_destination() == other.get_destination() and
                self.percents_barier == other.percents_barier)


class ActionIdlenessPrototype(ActionPrototype):

    TYPE = 'IDLENESS'
    TEXTGEN_TYPE = 'action_idleness'
    EXTRA_HELP_CHOICES = set((HELP_CHOICES.START_QUEST,))

    class STATE(ActionPrototype.STATE):
        QUEST = 'QUEST'
        IN_PLACE = 'IN_PLACE'
        WAITING = 'WAITING'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, parent=None, hero=None):
        if parent:
            model = Action.objects.create( type=cls.TYPE, parent=parent.model, hero=parent.hero.model, order=parent.order+1, state=cls.STATE.WAITING)
        else:
            model = Action.objects.create( type=cls.TYPE, hero=hero.model, order=0, percents=1.0, state=cls.STATE.WAITING)
        return cls(model=model)

    def init_quest(self):

        if self.state != self.STATE.WAITING:
            return False

        self.percents = 1.0

        self.updated = True

        return True

    def process(self):

        if self.state == self.STATE.IN_PLACE:
            self.state = self.STATE.WAITING
            self.percents = 0

        if self.state == self.STATE.QUEST:
            self.percents = 0
            self.state = self.STATE.IN_PLACE
            ActionInPlacePrototype.create(self)

        if self.state == self.STATE.WAITING:

            self.percents += 1.0 / c.TURNS_TO_IDLE

            if self.percents >= 1.0:
                self.state = self.STATE.QUEST
                quest = create_random_quest_for_hero(self.hero)
                ActionQuestPrototype.create(parent=self, quest=quest)
                self.percents = 0

            else:
                if random.uniform(0, 1) < 0.2:
                    self.hero.add_message('action_idleness_waiting', hero=self.hero)


class ActionQuestPrototype(ActionPrototype):

    TYPE = 'QUEST'
    TEXTGEN_TYPE = 'action_quest'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionPrototype.STATE):
        PROCESSING = 'processing'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, parent, quest):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       quest=quest.model,
                                       state=cls.STATE.PROCESSING)
        return cls(model=model)

    def process(self):

        if self.state == self.STATE.PROCESSING:
            percents = self.quest.process(self)

            self.percents = percents

            if self.percents >= 1:
                self.percents = 1
                self.state = self.STATE.PROCESSED


class ActionMoveToPrototype(ActionPrototype):

    TYPE = 'MOVE_TO'
    TEXTGEN_TYPE = 'action_moveto'
    SHORT_DESCRIPTION = u'путешествует'
    EXTRA_HELP_CHOICES = set((HELP_CHOICES.TELEPORT,))

    class STATE(ActionPrototype.STATE):
        CHOOSE_ROAD = 'choose_road'
        MOVING = 'moving'
        IN_CITY = 'in_city'
        BATTLE = 'battle'
        RESTING = 'resting'
        RESURRECT = 'resurrect'

    destination_id = ActionPrototype.place_id
    destination = ActionPrototype.place

    ###########################################
    # Object operations
    ###########################################


    @classmethod
    def _create(cls, parent, destination, break_at=None):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       place=destination.model,
                                       break_at=break_at,
                                       state=cls.STATE.CHOOSE_ROAD)
        parent.hero.add_message('action_moveto_start', hero=parent.hero, destination=destination)
        return cls(model=model)

    def get_description_arguments(self):
        args = super(ActionMoveToPrototype, self).get_description_arguments()
        args.update({'destination': self.place})
        return args

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

        self.hero.last_action_percents = self.percents

        self.updated = True

        return True

    @property
    def current_destination(self): return self.road.point_2 if not self.hero.position.invert_direction else self.road.point_1

    def process(self):

        if self.state == self.STATE.RESTING:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.RESURRECT:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.IN_CITY:
            self.state = self.STATE.CHOOSE_ROAD

        if self.state == self.STATE.BATTLE:
            if not self.hero.is_alive:
                ActionResurrectPrototype.create(self)
                self.state = self.STATE.RESURRECT
            else:
                if self.hero.need_rest_in_move:
                    ActionRestPrototype.create(self)
                    self.state = self.STATE.RESTING
                else:
                    self.state = self.STATE.MOVING

        if self.state == self.STATE.CHOOSE_ROAD:

            if self.hero.position.place_id:
                if self.hero.position.place_id != self.destination_id:
                    self.road, length = WaymarkPrototype.look_for_road(point_from=self.hero.position.place_id, point_to=self.destination_id)
                    self.hero.position.set_road(self.road, invert=(self.hero.position.place_id != self.road.point_1_id))
                    self.state = self.STATE.MOVING
                else:
                    length = None
                    self.percents = 1
                    self.state = self.STATE.PROCESSED
            else:
                road_left, length_left = WaymarkPrototype.look_for_road(point_from=self.hero.position.road.point_1_id, point_to=self.destination_id)
                road_right, length_right = WaymarkPrototype.look_for_road(point_from=self.hero.position.road.point_2_id, point_to=self.destination_id)

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
                    self.state = self.STATE.IN_CITY
                else:
                    self.road = self.hero.position.road
                    self.hero.position.set_road(self.hero.position.road, invert=invert, percents=percents)
                    self.state = self.STATE.MOVING

            if self.length is None:
                self.length = length


        if self.state == self.STATE.MOVING:

            current_destination = self.current_destination

            if random.uniform(0, 1) <= c.BATTLES_PER_TURN:
                mob = create_mob_for_hero(self.hero)
                ActionBattlePvE1x1Prototype.create(parent=self, mob=mob)
                self.state = self.STATE.BATTLE
            else:

                if random.uniform(0, 1) < 0.33:
                    self.hero.add_message('action_moveto_move',
                                          hero=self.hero,
                                          destination=self.destination,
                                          current_destination=self.current_destination)

                delta = self.hero.move_speed / self.road.length

                self.hero.position.percents += delta

                real_length = self.length if self.break_at is None else self.length * self.break_at
                self.percents += self.hero.move_speed / real_length

                if self.hero.position.percents >= 1:
                    self.hero.position.percents = 1
                    self.hero.position.set_place(current_destination)

                    self.state = self.STATE.IN_CITY

                    ActionInPlacePrototype.create(parent=self)

                elif self.break_at and self.percents >= 1:
                    self.percents = 1
                    self.state = self.STATE.PROCESSED


class ActionBattlePvE1x1Prototype(ActionPrototype):

    TYPE = 'BATTLE_PVE1x1'
    TEXTGEN_TYPE = 'action_battlepve1x1'
    CONTEXT_MANAGER = contexts.BattleContext
    EXTRA_HELP_CHOICES = set((HELP_CHOICES.LIGHTING,))

    class STATE(ActionPrototype.STATE):
        BATTLE_RUNNING = 'battle_running'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, parent, mob):

        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       mob=s11n.to_json(mob.serialize()),
                                       state=cls.STATE.BATTLE_RUNNING)
        parent.hero.add_message('action_battlepve1x1_start', hero=parent.hero, mob=mob)
        return cls(model=model)

    def get_description_arguments(self):
        args = super(ActionBattlePvE1x1Prototype, self).get_description_arguments()
        args.update({'mob': self.mob})
        return args

    def bit_mob(self, percents):

        if self.state != self.STATE.BATTLE_RUNNING:
            return False

        self.mob.strike_by(percents)

        self.percents = 1 - self.mob.health_percents
        self.hero.last_action_percents = self.percents

        self.updated = True

        return True

    def process(self, ):

        if self.state == self.STATE.BATTLE_RUNNING:
            battle.make_turn(battle.Actor(self.hero, self.context),
                             battle.Actor(self.mob, self.mob_context ),
                             self.hero)

            self.percents = 1.0 - self.mob.health_percents

            if self.hero.health <= 0:
                self.hero.kill()
                self.hero.statistics.change_pve_deaths(1)
                self.hero.add_message('action_battlepve1x1_hero_killed', important=True, hero=self.hero, mob=self.mob)
                self.state = self.STATE.PROCESSED
                self.percents = 1.0


            if self.mob.health <= 0:
                self.mob.kill()
                self.hero.statistics.change_pve_kills(1)
                self.hero.add_experience(c.EXP_PER_MOB * self.mob.exp_cooficient)
                self.hero.add_message('action_battlepve1x1_mob_killed', hero=self.hero, mob=self.mob)

                loot = self.mob.get_loot()

                if loot is not None:
                    bag_uuid = self.hero.put_loot(loot)

                    if bag_uuid is not None:
                        if loot.is_useless:
                            self.hero.statistics.change_loot_had(1)
                        else:
                            self.hero.statistics.change_artifacts_had(1)
                        self.hero.add_message('action_battlepve1x1_put_loot', hero=self.hero, artifact=loot)
                    else:
                        self.hero.add_message('action_battlepve1x1_put_loot_no_space', hero=self.hero, artifact=loot)
                else:
                    self.hero.add_message('action_battlepve1x1_no_loot', hero=self.hero)

                self.percents = 1.0
                self.state = self.STATE.PROCESSED

            if self.state == self.STATE.PROCESSED:
                self.remove_mob()


class ActionResurrectPrototype(ActionPrototype):

    TYPE = 'RESURRECT'
    TEXTGEN_TYPE = 'action_resurrect'
    EXTRA_HELP_CHOICES = set((HELP_CHOICES.RESURRECT,))

    class STATE(ActionPrototype.STATE):
        RESURRECT = 'resurrect'

    @classmethod
    def _create(cls, parent):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       state=cls.STATE.RESURRECT)
        return cls(model=model)

    def fast_resurrect(self):
        if self.state != self.STATE.RESURRECT:
            return False

        self.percents = 1.0
        self.hero.last_action_percents = self.percents

        self.updated = True
        return True


    def process(self):

        if self.state == self.STATE.RESURRECT:

            self.percents += 1.0 / c.TURNS_TO_RESURRECT

            if self.percents >= 1:
                self.percents = 1
                self.hero.resurrect()
                self.state = self.STATE.PROCESSED


class ActionInPlacePrototype(ActionPrototype):

    TYPE = 'IN_PLACE'
    TEXTGEN_TYPE = 'action_inplace'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionPrototype.STATE):
        SPEND_MONEY = 'spend_money'
        CHOOSING = 'choosing'
        TRADING = 'trading'
        RESTING = 'resting'
        EQUIPPING = 'equipping'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, parent):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       state=cls.STATE.SPEND_MONEY)
        return cls(model=model)

    def get_description_arguments(self):
        args = super(ActionInPlacePrototype, self).get_description_arguments()
        args.update({'place': self.hero.position.place})
        return args

    def process(self):

        if self.hero.position.place.is_settlement:
            return self.process_settlement()

    def try_to_spend_money(self, gold_amount, money_source):
        if gold_amount <= self.hero.money:
            gold_amount = min(self.hero.money, int(gold_amount * (1 + random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA))))
            gold_amount = self.hero.abilities.update_buy_price(self.hero, gold_amount)
            self.hero.change_money(money_source, -gold_amount)
            self.hero.switch_spending()
            return gold_amount

        return None

    def spend_money(self):

        if self.hero.next_spending == ITEMS_OF_EXPENDITURE.INSTANT_HEAL:
            coins = self.try_to_spend_money(f.instant_heal_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_HEAL)
            if coins is not None:
                self.hero.health = self.hero.max_health
                self.hero.add_message('action_inplace_instant_heal', important=True, hero=self.hero, coins=coins)

        elif self.hero.next_spending == ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT:
            coins = self.try_to_spend_money(f.buy_artifact_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_ARTIFACTS)
            if coins is not None:
                artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
                self.hero.bag.put_artifact(artifact)
                self.hero.statistics.change_artifacts_had(1)
                self.hero.add_message('action_inplace_buying_artifact', important=True, hero=self.hero, coins=coins, artifact=artifact)

        elif self.hero.next_spending == ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT:
            coins = self.try_to_spend_money(f.sharpening_artifact_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_SHARPENING)
            if coins is not None:
                # select filled slot
                choices = copy.copy(SLOTS_LIST)
                random.shuffle(choices)
                for slot in choices:
                    artifact = self.hero.equipment.get(slot)
                    if artifact is not None:
                        # sharpening artefact
                        artifact.power += 1
                        self.hero.equipment.updated = True
                        self.hero.add_message('action_inplace_sharpening_artifact', important=True, hero=self.hero, coins=coins, artifact=artifact)
                        break

        elif self.hero.next_spending == ITEMS_OF_EXPENDITURE.USELESS:
            coins = self.try_to_spend_money(f.useless_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_USELESS)
            if coins is not None:
                self.hero.add_message('action_inplace_spend_useless', important=True, hero=self.hero, coins=coins)

        elif self.hero.next_spending == ITEMS_OF_EXPENDITURE.IMPACT:
            coins = self.try_to_spend_money(f.impact_price(self.hero.level), MONEY_SOURCE.SPEND_FOR_IMPACT)
            if coins is not None:
                impact = f.impact_value(self.hero.level, 1)
                person = random.choice(self.hero.position.place.persons)
                if random.choice([True, False]):
                    workers_environment.highlevel.cmd_change_person_power(person.id, impact)
                    self.hero.add_message('action_inplace_impact_good', important=True, hero=self.hero, coins=coins, person=person)
                else:
                    workers_environment.highlevel.cmd_change_person_power(person.id, -impact)
                    self.hero.add_message('action_inplace_impact_bad', important=True, hero=self.hero, coins=coins, person=person)

        else:
            raise ActionException('wrong hero money spend type: %d' % self.hero.next_spending)


    def process_settlement(self):

        if self.state == self.STATE.SPEND_MONEY:
            self.state = self.STATE.CHOOSING
            self.spend_money()

        if self.state in [self.STATE.RESTING, self.STATE.EQUIPPING, self.STATE.TRADING]:
            self.state = self.STATE.CHOOSING

        if self.state == self.STATE.CHOOSING:
            if self.hero.need_rest_in_settlement:
                self.state = self.STATE.RESTING
                ActionRestPrototype.create(self)

            elif self.hero.need_equipping_in_town:
                self.state = self.STATE.EQUIPPING
                ActionEquippingPrototype.create(self)

            elif self.hero.need_trade_in_town:
                self.state = self.STATE.TRADING
                ActionTradingPrototype.create(self)

            else:
                self.state = self.STATE.PROCESSED


class ActionRestPrototype(ActionPrototype):

    TYPE = 'REST'
    TEXTGEN_TYPE = 'action_rest'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionPrototype.STATE):
        RESTING = 'resting'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, parent):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       state=cls.STATE.RESTING)
        parent.hero.add_message('action_rest_start', hero=parent.hero)
        return cls(model=model)

    def process(self):

        if self.state == self.STATE.RESTING:
            heal_amount = int(round(float(self.hero.max_health) / c.HEAL_LENGTH * (1 + random.uniform(-c.HEAL_STEP_FRACTION, c.HEAL_STEP_FRACTION))))

            heal_amount = self.hero.heal(heal_amount)

            if random.uniform(0, 1) < 0.2:
                self.hero.add_message('action_rest_resring', hero=self.hero, health=heal_amount)

            self.percents = float(self.hero.health)/self.hero.max_health

            if self.hero.health == self.hero.max_health:
                self.state = self.STATE.PROCESSED


class ActionEquippingPrototype(ActionPrototype):

    TYPE = 'EQUIPPING'
    TEXTGEN_TYPE = 'action_equipping'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionPrototype.STATE):
        EQUIPPING = 'equipping'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, parent):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       state=cls.STATE.EQUIPPING)
        return cls(model=model)

    def process(self):

        if self.state == self.STATE.EQUIPPING:
            # TODO: calculate real percents
            self.percents = min(self.percents+0.25, 1)

            slot, unequipped, equipped = self.hero.get_equip_canditates()
            self.hero.change_equipment(slot, unequipped, equipped)
            if equipped:
                if unequipped:
                    if equipped.id == unequipped.id:
                        self.hero.add_message('action_equipping_change_equal_items', important=True, hero=self.hero, item=equipped)
                    else:
                        self.hero.add_message('action_equipping_change_item', important=True, hero=self.hero, unequipped=unequipped, equipped=equipped)
                else:
                    self.hero.add_message('action_equipping_equip_item', important=True, hero=self.hero, equipped=equipped)
            else:
                self.state = self.STATE.PROCESSED


class ActionTradingPrototype(ActionPrototype):

    TYPE = 'TRADING'
    TEXTGEN_TYPE = 'action_trading'
    SHORT_DESCRIPTION = u'торгует'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionPrototype.STATE):
        TRADING = 'trading'

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        # TODO: move to parent class
        info = super(ActionTradingPrototype, self).ui_info()
        info['data'] = {'hero_id': self.hero_id}
        return info

    @classmethod
    def _create(cls, parent):
        model = Action.objects.create( type=cls.TYPE,
                                       parent=parent.model,
                                       hero=parent.hero.model,
                                       order=parent.order+1,
                                       percents_barier=parent.hero.bag.occupation[1],
                                       state=cls.STATE.TRADING)
        parent.hero.add_message('action_trading_start', hero=parent.hero)
        return cls(model=model)


    def get_sell_price(self, artifact):
        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        if artifact.is_useless:
            if artifact.rarity == RARITY_TYPE.NORMAL:
                gold_amount = 1 + int(f.normal_loot_cost_at_lvl(artifact.level) * multiplier)
            elif artifact.rarity == RARITY_TYPE.RARE:
                gold_amount = 1 + int(f.rare_loot_cost_at_lvl(artifact.level) * multiplier)
            elif artifact.rarity == RARITY_TYPE.EPIC:
                gold_amount = 1 + int(f.epic_loot_cost_at_lvl(artifact.level) * multiplier)
            else:
                raise ActionException('unknown artifact rarity type: %s' % artifact)
        else:
            gold_amount = 1 + int(f.sell_artifact_price(artifact.level) * multiplier)

        return self.hero.abilities.update_sell_price(self.hero, gold_amount)


    def process(self):

        if self.state == self.STATE.TRADING:
            quest_items_count, loot_items_count = self.hero.bag.occupation

            if loot_items_count:

                self.percents = 1 - float(loot_items_count - 1) / self.percents_barier

                for item in self.hero.bag.items():
                    artifact_uuid, artifact = item
                    if not artifact.quest:
                        break

                sell_price = self.get_sell_price(artifact)

                if artifact.is_useless:
                    money_source = MONEY_SOURCE.EARNED_FROM_LOOT
                else:
                    money_source = MONEY_SOURCE.EARNED_FROM_ARTIFACTS

                self.hero.change_money(money_source, sell_price)
                self.hero.bag.pop_artifact(artifact)

                self.hero.add_message('action_trading_sell_item', hero=self.hero, artifact=artifact, coins=sell_price)

            if loot_items_count <= 1:
                self.state = self.STATE.PROCESSED


class ActionMoveNearPlacePrototype(ActionPrototype):

    TYPE = 'MOVE_NEAR_PLACE'
    TEXTGEN_TYPE = 'action_movenearplace'
    EXTRA_HELP_CHOICES = set()

    class STATE(ActionPrototype.STATE):
        MOVING = 'MOVING'
        BATTLE = 'BATTLE'
        RESTING = 'RESTING'
        RESURRECT = 'RESURRECT'

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        info = super(ActionMoveNearPlacePrototype, self).ui_info()
        return info

    @classmethod
    def _create(cls, parent, place, back):

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
                                       destination_y=y,
                                       state=cls.STATE.MOVING)

        if parent.hero.position.is_walking:
            from_x, from_y = parent.hero.position.coordinates_to
            parent.hero.position.set_coordinates(from_x, from_y, x, y, percents=0)
        else:
            parent.hero.position.set_coordinates(place.x, place.y, x, y, percents=0)

        return cls(model=model)

    def get_description_arguments(self):
        args = super(ActionMoveNearPlacePrototype, self).get_description_arguments()
        args.update({'place': self.place})
        return args

    def process(self):

        if self.state == self.STATE.RESTING:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.RESURRECT:
            self.state = self.STATE.MOVING

        if self.state == self.STATE.BATTLE:
            if not self.hero.is_alive:
                ActionResurrectPrototype.create(self)
                self.state = self.STATE.RESURRECT
            else:
                if self.hero.need_rest_in_move:
                    ActionRestPrototype.create(self)
                    self.state = self.STATE.RESTING
                else:
                    self.state = self.STATE.MOVING

        if self.state == self.STATE.MOVING:

            if random.uniform(0, 1) <= c.BATTLES_PER_TURN:
                mob = create_mob_for_hero(self.hero)
                ActionBattlePvE1x1Prototype.create(parent=self, mob=mob)
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
                    self.hero.position.percents = 1
                    self.percents = 1

                    to_x, to_y = self.hero.position.coordinates_to
                    if self.place.x == to_x and self.place.y == to_y:
                        self.hero.position.set_place(self.place)

                    self.state = self.STATE.PROCESSED


ACTION_TYPES = get_actions_types()
