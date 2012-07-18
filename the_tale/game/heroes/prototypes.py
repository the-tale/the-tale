# -*- coding: utf-8 -*-
import math
import time
import datetime
import random

from django.utils.log import getLogger
from django.conf import settings as project_settings

from dext.utils import s11n
from dext.utils import database

from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage

from game.game_info import GENDER, RACE_CHOICES, GENDER_ID_2_STR, ITEMS_OF_EXPENDITURE, GENDER_DICT_USERFRIENDLY, RACE_DICT, ATTRIBUTES

from game import names

from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS
from game.heroes.statistics import HeroStatistics
from game.heroes.preferences import HeroPreferences
from game.heroes.models import Hero, ChooseAbilityTask, CHOOSE_ABILITY_STATE
from game.heroes.habilities import AbilitiesPrototype, ABILITIES
from game.heroes.conf import heroes_settings

from game.map.prototypes import MapInfoPrototype

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

from game.balance import constants as c, formulas as f
from game.prototypes import TimePrototype, GameTime

logger=getLogger('the-tale.workers.game_logic')

class HeroPrototype(object):

    def __init__(self, model=None):
        self.model = model
        self.messages_updated = False
        self.diary_updated = False
        self.actions_descriptions_updated = False

    @classmethod
    def get_by_id(cls, model_id):
        try:
            return cls(model=Hero.objects.get(id=model_id))
        except Hero.DoesNotExist:
            return None

    @classmethod
    def get_by_angel_id(cls, angel_id):
        try:
            return cls(model=Hero.objects.get(angel_id=angel_id))
        except Hero.DoesNotExist:
            return None


    def get_is_alive(self): return self.model.alive
    def set_is_alive(self, value): self.model.alive = value
    is_alive = property(get_is_alive, set_is_alive)

    @property
    def id(self): return self.model.id

    @property
    def angel_id(self): return self.model.angel_id

    @property
    def created_at_turn(self): return self.model.created_at_turn

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
    def basic_damage(self): return f.damage_from_power(self.power) * self.damage_modifier

    @property
    def race(self): return self.model.race

    @property
    def level(self): return self.model.level

    @property
    def experience(self): return self.model.experience
    def add_experience(self, value):
        self.model.experience += value
        while f.exp_on_lvl(self.level) <= self.model.experience:
            self.model.experience -= f.exp_on_lvl(self.level)
            self.model.level += 1
            if self.model.level % c.DESTINY_POINT_IN_LEVELS == 0:
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

    @property
    def money(self): return self.model.money

    def change_money(self, source, value):
        self.statistics.change_money(source, abs(value))
        self.model.money += value

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
    def damage_modifier(self): return self.abilities.modify_attribute(ATTRIBUTES.DAMAGE, 1)

    @property
    def move_speed(self): return 0.3

    @property
    def initiative(self): return self.abilities.modify_attribute(ATTRIBUTES.INITIATIVE, 1)

    @property
    def max_health(self): return int(f.hp_on_lvl(self.level) * self.abilities.modify_attribute(ATTRIBUTES.HEALTH, 1))

    @property
    def max_bag_size(self): return c.MAX_BAG_SIZE

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
    # actions
    ###########################################p

    def get_actions(self):
        #TODO: now this code only works on bundle init phase
        #      using it from another places is dangerouse becouse of
        #      desinchronization between workers and database
        from game.actions.models import Action
        from game.actions.prototypes import ACTION_TYPES

        actions = []
        actions_models = list(Action.objects.filter(hero=self.model).order_by('order'))
        for action in actions_models:
            action_object = ACTION_TYPES[action.type](model=action)
            actions.append(action_object)

        return actions

    @property
    def position(self):
        if not hasattr(self, '_position'):
            self._position = HeroPositionPrototype(hero_model=self.model)
        return self._position

    @property
    def statistics(self):
        if not hasattr(self, '_statistics'):
            self._statistics = HeroStatistics(hero_model=self.model)
        return self._statistics

    @property
    def preferences(self):
        if not hasattr(self, '_preferences'):
            self._preferences = HeroPreferences(hero_model=self.model)
        return self._preferences

    def get_last_action_percents(self): return self.model.last_action_percents
    def set_last_action_percents(self, value): self.model.last_action_percents = value
    last_action_percents = property(get_last_action_percents, set_last_action_percents)

    @property
    def actions_descriptions(self):
        if not hasattr(self, '_actions_descriptions'):
            self._actions_descriptions = s11n.from_json(self.model.actions_descriptions)
        return self._actions_descriptions

    def push_action_description(self, description):
        self.actions_descriptions_updated = True
        self.actions_descriptions.append(description)

    def pop_action_description(self):
        self.actions_descriptions_updated = True
        self.actions_descriptions.pop()

    @property
    def messages(self):
        if not hasattr(self, '_messages'):
            self._messages = s11n.from_json(self.model.messages)
        return self._messages

    @property
    def diary(self):
        if not hasattr(self, '_diary'):
            self._diary = s11n.from_json(self.model.diary)
        return self._diary

    def push_message(self, msg, important=False):
        self.messages_updated = True
        self.messages.append(msg)
        if len(self.messages) > heroes_settings.MESSAGES_LOG_LENGTH:
            self.messages.pop(0)

        if important:
            self.diary_updated = True
            self.diary.append(msg)
            if len(self.diary) > heroes_settings.MESSAGES_LOG_LENGTH:
                self.diary.pop(0)

    @staticmethod
    def _prepair_message(msg, in_past=0):
        return (TimePrototype.get_current_turn_number()-in_past, time.mktime(datetime.datetime.now().timetuple())-in_past*c.TURN_DELTA, msg)

    def add_message(self, type_, important=False, **kwargs):
        args = prepair_substitution(kwargs)
        template = get_vocabulary().get_random_phrase(type_)

        if template is None:
            if not project_settings.TESTS_RUNNING:
                logger.error('hero:add_message: unknown template type: %s' % type_)
            return
        msg = template.substitute(get_dictionary(), args)
        self.push_message(self._prepair_message(msg), important=important)


    def heal(self, delta):
        old_health = self.health
        self.health = min(self.health + int(delta), self.max_health)
        return self.health - old_health

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        for action in reversed(self.get_actions()):
            action.remove(force=True)
        self.model.delete()

    def save(self):
        if self.bag.updated:
            self.model.bag = s11n.to_json(self.bag.serialize())
            self.bag.updated = False

        if self.equipment.updated:
            self.model.equipment = s11n.to_json(self.equipment.serialize())
            self.equipment.updated = False

        if self.abilities.updated:
            self.model.abilities = s11n.to_json(self.abilities.serialize())
            self.abilities.updated = False

        if self.messages_updated:
            self.model.messages = s11n.to_json(self.messages)
            self.messages_updated = False

        if self.diary_updated:
            self.model.diary = s11n.to_json(self.diary)
            self.diary_updated = False

        if self.actions_descriptions_updated:
            self.model.actions_descriptions = s11n.to_json(self.actions_descriptions)
            self.actions_descriptions_updated = False

        database.raw_save(self.model)

    @staticmethod
    def _compare_messages(first, second):
        if len(first) != len(second):
            return False

        for a,b in zip(first, second):
            if a[0] != b[0] or a[2] != b[2] or abs(a[1] - b[1]) > 0.0001:
                return False

        return True

    def __eq__(self, other):

        return (self.id == other.id and
                self.is_alive == other.is_alive and
                self.angel_id == other.angel_id and
                self.name == other.name and
                self.gender == other.gender and
                self.race == other.race and
                self.level == other.level and
                self.last_action_percents == other.last_action_percents and
                self.experience == other.experience and
                self.destiny_points == other.destiny_points and
                self.health == other.health and
                self.money == other.money and
                self.abilities == other.abilities and
                self.bag == other.bag and
                self.equipment == other.equipment and
                self.next_spending == other.next_spending and
                self.position == other.position and
                self.statistics == other.statistics and
                self._compare_messages(self.messages, other.messages) and
                self._compare_messages(self.diary, other.diary) and
                self.actions_descriptions == other.actions_descriptions)

    def ui_info(self, ignore_actions=False):

        quest_items_count, loot_items_count = self.bag.occupation

        messages = []
        for turn_number, timestamp, msg in self.messages:
            game_time = GameTime.create_from_turn(turn_number)
            messages.append((timestamp, game_time.verbose_time, msg))

        diary = []
        for turn_number, timestamp, msg in self.diary:
            game_time = GameTime.create_from_turn(turn_number)
            diary.append((timestamp, game_time.verbose_date, game_time.verbose_time, msg))

        return {'id': self.id,
                'angel': self.angel_id,
                'messages': messages,
                'diary': diary,
                'position': self.position.ui_info(),
                'alive': self.is_alive,
                'bag': self.bag.ui_info(),
                'equipment': self.equipment.ui_info(),
                'money': self.money,
                'action': { 'percents': self.last_action_percents,
                            'description': self.actions_descriptions[-1]},
                'base': { 'name': self.name,
                          'level': self.level,
                          'destiny_points': self.destiny_points,
                          'health': self.health,
                          'max_health': self.max_health,
                          'experience': self.experience * c.EXP_MULTIPLICATOR,
                          'experience_to_level': f.exp_on_lvl(self.level) * c.EXP_MULTIPLICATOR,
                          'gender': GENDER_DICT_USERFRIENDLY[self.gender],
                          'race': RACE_DICT[self.race] },
                'secondary': { 'power': math.floor(self.power),
                               'move_speed': self.move_speed,
                               'initiative': self.initiative,
                               'max_bag_size': self.max_bag_size,
                               'loot_items_count': loot_items_count,
                               'quest_items_count': quest_items_count},
                'accumulated': { }
                }


    @classmethod
    def create(cls, angel, bundle):

        from game.actions.prototypes import ActionIdlenessPrototype

        start_place = places_storage.random_place()

        race = random.choice(RACE_CHOICES)[0]

        gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

        hero = Hero.objects.create(created_at_turn=TimePrototype.get_current_turn_number(),
                                   angel=angel.model,
                                   gender=gender,
                                   race=race,
                                   messages=s11n.to_json([cls._prepair_message(u'Тучи сгущаются (и как быстро!), к непогоде...', in_past=7),
                                                          cls._prepair_message(u'Аааааа, по всюду молниции, спрячусь ка я под этим большим дубом.', in_past=6),
                                                          cls._prepair_message(u'Бабах!!!', in_past=5),
                                                          cls._prepair_message(u'Темно, страшно, кажется, я в коридоре...', in_past=4),
                                                          cls._prepair_message(u'Свет! Надо идти на свет!', in_past=3),
                                                          cls._prepair_message(u'Свет сказал, что избрал меня для великих дел, взял кровь из пальца и поставил ей крестик в каком-то пергаменте.', in_past=2),
                                                          cls._prepair_message(u'Приказано идти обратно и геройствовать, как именно геройствовать - не уточняется', in_past=1),
                                                          cls._prepair_message(u'Эх, опять в этом мире, в том было хотя бы чисто и сухо. Голова болит. Палец болит. Тянет на подвиги.', in_past=0)]),
                                   diary=s11n.to_json([cls._prepair_message(u'Вот жеж угораздило. У всех ангелы-хранители нормальные, сидят себе и попаданию подопечных в загробный мир не мешают. А у моего, значит, шило в заднице! Где ты был, когда я лотерейные билеты покупал?! Молнию отвести он значит не может, а воскресить - запросто. Как же всё болит, кажется теперь у меня две печёнки (это, конечно, тебе спасибо, всегда пригодится). Ну ничего, рано или поздно я к твоему начальству попаду и там уж всё расскажу! А пока буду записывать в свой дневник.')]),
                                   name=names.generator.get_name(race, gender),
                                   health=f.hp_on_lvl(1),
                                   pos_place = start_place.model)

        hero = cls(model=hero)

        bundle.add_hero(hero)

        ActionIdlenessPrototype.create(parent=None, hero=hero, _bundle=bundle)

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

    def process_turn(self):
        return TimePrototype.get_current_turn_number() + 1



class HeroPositionPrototype(object):

    def __init__(self, hero_model, *argv, **kwargs):
        self.hero_model = hero_model

    @property
    def place_id(self): return self.hero_model.pos_place_id

    @property
    def place(self): return places_storage.get(self.hero_model.pos_place_id)

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
    def road_id(self): return self.hero_model.pos_road_id

    @property
    def road(self): return roads_storage.get(self.hero_model.pos_road_id)

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

    def __eq__(self, other):
        return ( self.place_id == other.place_id and
                 self.road_id == other.road_id and
                 self.percents == other.percents and
                 self.invert_direction == other.invert_direction and
                 self.coordinates_from == other.coordinates_from and
                 self.coordinates_to == other.coordinates_to)


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

    def process(self, bundle):

        hero = bundle.heroes[self.hero_id]

        if self.ability_id not in ABILITIES:
            self.state = CHOOSE_ABILITY_STATE.ERROR
            self.comment = u'no ability with id "%s"' % self.ability_id
            return

        choices = hero.get_abilities_for_choose()

        if self.ability_id not in [choice.get_id() for choice in choices]:
            self.state = CHOOSE_ABILITY_STATE .ERROR
            self.comment = u'ability not in choices list: %s' % self.ability_id
            return

        ability = ABILITIES[self.ability_id]

        if not ability.AVAILABLE_TO_PLAYERS:
            self.state = CHOOSE_ABILITY_STATE.ERROR
            self.comment = u'ability "%s" does not available to players' % self.ability_id
            return

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
