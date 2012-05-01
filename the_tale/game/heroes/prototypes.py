# -*- coding: utf-8 -*-
import math
import random
import numbers

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from game.map.places.prototypes import PlacePrototype
from game.map.roads.prototypes import RoadPrototype

from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS

from game.textgen import get_vocabulary, get_dictionary
from game.textgen.words import Fake as FakeWord
from game.game_info import GENDER, RACE_CHOICES, GENDER_ID_2_STR, ITEMS_OF_EXPENDITURE

from .. import names

from ..quests.prototypes import get_quest_by_model
from ..quests.models import Quest

from .models import Hero, ChooseAbilityTask, CHOOSE_ABILITY_STATE
from .habilities import AbilitiesPrototype
from .conf import heroes_settings

from ..map.prototypes import MapInfoPrototype

from game.balance import constants as c, formulas as f


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
    def name(self): return self.model.name

    @property
    def gender(self): return self.model.gender

    @property
    def power(self): return f.clean_power_to_lvl(self.level) + self.equipment.get_power()

    @property
    def basic_damage(self): return f.damage_from_power(self.power)

    @property
    def race(self): return self.model.race

    @property
    def level(self): return self.model.level

    @property
    def experience(self): return self.model.experience
    def add_experience(self, value):
        self.model.experience += value
        while self.experience_to_level <= self.model.experience:
            self.model.experience -= self.experience_to_level
            self.model.level += 1
            if self.model.level % 2:
                self.model.destiny_points += 1

    def get_destiny_points(self): return self.model.destiny_points
    def set_destiny_points(self, value): self.model.destiny_points = value
    destiny_points = property(get_destiny_points, set_destiny_points)

    def get_destiny_points_spend(self): return self.model.destiny_points_spend
    def set_destiny_points_spend(self, value): self.model.destiny_points_spend = value
    destiny_points_spend = property(get_destiny_points_spend, set_destiny_points_spend)


    def get_health(self): return self.model.health
    def set_health(self, value): self.model.health = value
    health = property(get_health, set_health)

    def get_money(self): return self.model.money
    def set_money(self, value): self.model.money = value
    money = property(get_money, set_money)

    @property
    def abilities(self):
        if not hasattr(self, '_abilities'):
            self._abilities = AbilitiesPrototype.deserialize(s11n.from_json(self.model.abilities))
        return self._abilities

    def get_abilities_for_choose(self):
        return self.abilities.get_for_choose(self)

    @property
    def bag(self):
        if not hasattr(self, '_bag'):
            from .bag import Bag
            self._bag = Bag()
            self._bag.deserialize(s11n.from_json(self.model.bag))
        return self._bag

    @property
    def bag_is_full(self):
        quest_items_count, loot_items_count = self.bag.occupation
        return loot_items_count >= self.max_bag_size

    def put_loot(self, artifact):
        if artifact.quest or not self.bag_is_full:
            self.bag.put_artifact(artifact)
            return artifact.bag_uuid


    def pop_loot(self, artifact):
        self.bag.pop_artifact(artifact)

    def pop_quest_loot(self, artifact):
        self.bag.pop_quest_artifact(artifact)

    def get_equip_canditates(self):

        equipped_slot = None
        equipped = None
        unequipped = None
        for uuid, artifact in self.bag.items():
            if not artifact.can_be_equipped or artifact.equip_type is None:
                continue

            for slot in ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type]:
                equipped_artifact = self.equipment.get(slot)
                if equipped_artifact is None:
                    equipped_slot = slot
                    equipped = artifact
                    break

            if equipped:
                break

            for slot in ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type]:
                equipped_artifact = self.equipment.get(slot)

                if equipped_artifact.power < artifact.power:
                    equipped = artifact
                    unequipped = equipped_artifact
                    equipped_slot = slot
                    break

            if equipped:
                break

        return equipped_slot, unequipped, equipped


    def change_equipment(self, slot, unequipped, equipped):
        if unequipped:
            self.equipment.unequip(slot)
            self.bag.put_artifact(unequipped)

        if equipped:
            self.bag.pop_artifact(equipped)
            self.equipment.equip(slot, equipped)


    @property
    def equipment(self):
        if not hasattr(self, '_equipment'):
            from .bag import Equipment
            self._equipment = Equipment()
            self._equipment.deserialize(s11n.from_json(self.model.equipment))
        return self._equipment

    @property
    def normalized_name(self):
        if self.gender == GENDER.MASCULINE:
            return (u'герой', GENDER_ID_2_STR[self.gender])
        elif self.gender == GENDER.FEMININE:
            return (u'героиня', GENDER_ID_2_STR[self.gender])

    @property
    def next_spending(self): return self.model.next_spending

    def switch_spending(self):
        self.model.next_spending = random.choice(ITEMS_OF_EXPENDITURE.ALL)


    ###########################################
    # Secondary attributes
    ###########################################

    @property
    def move_speed(self): return 0.3

    @property
    def initiative(self): return 1.0

    @property
    def max_health(self): return f.hp_on_lvl(self.level)

    @property
    def min_damage(self):
        damage = 5
        damage += self.equipment.get_attr_damage()[0]
        return damage

    @property
    def max_damage(self):
        damage = 10
        damage += self.equipment.get_attr_damage()[1]
        return damage

    @property
    def max_bag_size(self): return c.MAX_BAG_SIZE

    @property
    def experience_to_level(self):
        return 100 + (self.level - 1) * 100

    ###########################################
    # Needs attributes
    ###########################################

    @property
    def need_rest_in_settlement(self): return self.health < self.max_health * c.HEALTH_IN_SETTLEMENT_TO_START_HEAL_FRACTION

    @property
    def need_rest_in_move(self): return self.health < self.max_health * c.HEALTH_IN_MOVE_TO_START_HEAL_FRACTION

    @property
    def need_trade_in_town(self):
        quest_items_count, loot_items_count = self.bag.occupation
        return float(loot_items_count) / self.max_bag_size > c.BAG_SIZE_TO_SELL_LOOT_FRACTION

    @property
    def need_equipping_in_town(self):
        slot, unequipped, equipped = self.get_equip_canditates()
        return equipped is not None

    ###########################################
    # quests
    ###########################################

    @property
    def quest(self):
        try:
            return get_quest_by_model(Quest.objects.get(hero=self.model))
        except Quest.DoesNotExist:
            return None

    ###########################################
    # actions
    ###########################################p

    def get_actions(self):
        #TODO: now this code only works on bundle init phase
        #      using it from another places is dangerouse becouse of
        #      desinchronization between workers and database
        from game.actions.models import Action
        from game.actions.prototypes import ACTION_TYPES

        if not hasattr(self, '_actions'):
            self._actions = []
            actions = list(Action.objects.filter(hero=self.model).order_by('order'))
            for action in actions:
                action_object = ACTION_TYPES[action.type](model=action)
                self._actions.append(action_object)

        return self._actions

    @property
    def position(self):
        if not hasattr(self, '_position'):
            self._position = HeroPositionPrototype(hero_model=self.model)
        return self._position

    @property
    def messages(self):
        if not hasattr(self, '_messages'):
            self._messages = s11n.from_json(self.model.messages)
        return self._messages

    def push_message(self, msg):
        self.messages.append(msg)
        if len(self.messages) > heroes_settings.MESSAGES_LOG_LENGTH:
            self.messages.pop(0)

    def add_message(self, type_, **kwargs):
        args = {}
        for k, v in kwargs.items():
            if isinstance(v, (FakeWord, numbers.Number)):
                args[k] = v
            else:
                args[k] = v.normalized_name
        template = get_vocabulary().get_random_phrase(type_)
        if template is None:
            return
            # TODO: raise exception in production (not when tests running)
            # from game.textgen.exceptions import TextgenException
            # raise TextgenException(u'ERROR: unknown template type: %s' % type_)
        msg = template.substitute(get_dictionary(), args)
        # print msg
        self.push_message(msg)

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self):
        self.model.bag = s11n.to_json(self.bag.serialize())
        self.model.equipment = s11n.to_json(self.equipment.serialize())
        self.model.abilities = s11n.to_json(self.abilities.serialize())
        self.model.messages = s11n.to_json(self.messages)
        self.model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):

        quest_items_count, loot_items_count = self.bag.occupation

        return {'id': self.id,
                'angel': self.angel_id,
                'actions': [ action.ui_info() for action in self.get_actions() ] if not ignore_actions else [],
                'quests': self.quest.ui_info(self) if self.quest else {},
                'messages': self.messages,
                'position': self.position.ui_info(),
                'alive': self.is_alive,
                'bag': self.bag.ui_info(),
                'equipment': self.equipment.ui_info(),
                'money': self.money,
                'base': { 'name': self.name,
                          'level': self.level,
                          'destiny_points': self.destiny_points,
                          'health': self.health,
                          'max_health': self.max_health,
                          'experience': self.experience,
                          'experience_to_level': self.experience_to_level},
                'secondary': { 'power': math.floor(self.power),
                               'move_speed': self.move_speed,
                               'initiative': self.initiative,
                               'max_bag_size': self.max_bag_size,
                               'loot_items_count': loot_items_count},
                'accumulated': { }
                }


    @classmethod
    @nested_commit_on_success
    def create(cls, angel):
        from game.actions.prototypes import ActionIdlenessPrototype

        start_place = PlacePrototype.random_place()

        race = random.choice(RACE_CHOICES)[0]

        gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

        hero = Hero.objects.create(angel=angel.model,
                                   gender=gender,
                                   race=race,
                                   name=names.generator.get_name(race, gender),
                                   health=f.hp_on_lvl(1),
                                   pos_place = start_place.model)

        hero = cls(model=hero)

        ActionIdlenessPrototype.create(hero=hero)

        return hero

    ###########################################
    # Game operations
    ###########################################

    def kill(self):
        self.health = 1
        self.is_alive = False

    def resurrect(self):
        self.health = self.max_health
        self.is_alive = True

    ###########################################
    # Next turn operations
    ###########################################

    def process_turn(self, turn_number):
        return turn_number + 1



class HeroPositionPrototype(object):

    def __init__(self, hero_model, *argv, **kwargs):
        self.hero_model = hero_model

    @property
    def place_id(self): return self.hero_model.pos_place_id

    @property
    def place(self):
        if not hasattr(self, '_place'):
            self._place = PlacePrototype(model=self.hero_model.pos_place) if self.hero_model.pos_place else None
        return self._place

    def _reset_position(self):
        if hasattr(self, '_place'):
            delattr(self, '_place')
        if hasattr(self, '_road'):
            delattr(self, '_road')
        self.hero_model.pos_place = None
        self.hero_model.pos_road = None
        self.hero_model.pos_invert_direction = None
        self.hero_model.pos_percents = None
        self.hero_model.pos_from_x = None
        self.hero_model.pos_from_y = None
        self.hero_model.pos_to_x = None
        self.hero_model.pos_to_y = None

    def set_place(self, place):
        self._reset_position()
        self.hero_model.pos_place = place.model

    @property
    def road(self):
        if not hasattr(self, '_road'):
            self._road = RoadPrototype(model=self.hero_model.pos_road) if self.hero_model.pos_road else None
        return self._road

    def set_road(self, road, percents=0, invert=False):
        self._reset_position()
        self.hero_model.pos_road = road.model
        self.hero_model.pos_invert_direction = invert
        self.hero_model.pos_percents = percents

    def get_percents(self): return self.hero_model.pos_percents
    def set_percents(self, value): self.hero_model.pos_percents = value
    percents = property(get_percents, set_percents)

    def get_invert_direction(self): return self.hero_model.pos_invert_direction
    def set_invert_direction(self, value): self.hero_model.pos_invert_direction = value
    invert_direction = property(get_invert_direction, set_invert_direction)

    @property
    def coordinates_from(self): return self.hero_model.pos_from_x, self.hero_model.pos_from_y

    @property
    def coordinates_to(self): return self.hero_model.pos_to_x, self.hero_model.pos_to_y

    def subroad_len(self): return math.sqrt( (self.hero_model.pos_from_x-self.hero_model.pos_to_x)**2 +
                                             (self.hero_model.pos_from_y-self.hero_model.pos_to_y)**2)

    def set_coordinates(self, from_x, from_y, to_x, to_y, percents):
        self._reset_position()
        self.hero_model.pos_from_x = from_x
        self.hero_model.pos_from_y = from_y
        self.hero_model.pos_to_x = to_x
        self.hero_model.pos_to_y = to_y
        self.hero_model.pos_percents = percents

    @property
    def is_walking(self):
        return (self.hero_model.pos_from_x is not None and
                self.hero_model.pos_from_y is not None and
                self.hero_model.pos_to_x is not None and
                self.hero_model.pos_to_y is not None)

    @property
    def cell_coordinates(self):
        if self.place:
            return self.get_cell_coordinates_in_place()
        elif self.road:
            return self.get_cell_coordinates_on_road()
        else:
            return self.get_cell_coordinates_near_place()


    def get_cell_coordinates_in_place(self):
        return self.place.x, self.place.y

    def get_cell_coordinates_on_road(self):
        point_1 = self.road.point_1
        point_2 = self.road.point_2

        percents = self.percents;

        if self.invert_direction:
            percents = 1 - percents

        x = point_1.x + (point_2.x - point_1.x) * percents
        y = point_1.y + (point_2.y - point_1.y) * percents

        return int(x), int(y)

    def get_cell_coordinates_near_place(self):
        from_x, from_y = self.coordinates_from
        to_x, to_y = self.coordinates_to
        percents = self.percents

        x = from_x + (to_x - from_x) * percents
        y = from_y + (to_y - from_y) * percents

        return int(x), int(y)

    def get_terrain(self):
        map_info = MapInfoPrototype.get_latest()
        x, y = self.cell_coordinates
        return map_info.terrain[y][x]

    ###########################################
    # Checks
    ###########################################

    @property
    def is_settlement(self): return self.place and self.place.is_settlement

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        return {'place': self.place.map_info() if self.place else None,
                'road': self.road.map_info() if self.road else None,
                'invert_direction': self.invert_direction,
                'percents': self.percents,
                'coordinates': { 'to': { 'x': self.coordinates_to[0],
                                         'y': self.coordinates_to[1]},
                                 'from': { 'x': self.coordinates_from[0],
                                           'y': self.coordinates_from[1]} } }



class ChooseAbilityTaskPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, task_id):
        return cls(ChooseAbilityTask.objects.get(id=task_id))

    @classmethod
    def reset_all(cls):
        ChooseAbilityTask.objects.filter(state=CHOOSE_ABILITY_STATE.WAITING).update(state=CHOOSE_ABILITY_STATE.RESET)

    @property
    def id(self): return self.model.id

    def get_state(self): return self.model.state
    def set_state(self, value): self.model.state = value
    state = property(get_state, set_state)

    def get_comment(self): return self.model.comment
    def set_comment(self, value): self.model.comment = value
    comment = property(get_comment, set_comment)

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def ability_id(self): return self.model.ability_id

    @classmethod
    def create(cls, ability_id, hero_id):
        model = ChooseAbilityTask.objects.create(hero_id=hero_id,
                                                 ability_id=ability_id)
        return cls(model)

    def save(self):
        self.model.save()

    @nested_commit_on_success
    def process(self, bundle):

        hero = bundle.heroes[self.hero_id]

        if hero.destiny_points <= 0:
            self.state = CHOOSE_ABILITY_STATE.ERROR
            self.comment = 'no destiny points'
            return

        if hero.abilities.has(self.ability_id):

            self.state = CHOOSE_ABILITY_STATE.ERROR
            self.comment = 'ability has been already choosen'
            return

        else:
            hero.abilities.add(self.ability_id)

        hero.destiny_points -= 1
        hero.destiny_points_spend += 1

        self.state = CHOOSE_ABILITY_STATE.PROCESSED
