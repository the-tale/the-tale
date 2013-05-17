# coding: utf-8
import math
import datetime
import random
import copy

from textgen.words import Noun

from dext.utils import s11n, database, cache

from common.utils.prototypes import BasePrototype
from common.utils.logic import random_value_by_priority
from common.utils.decorators import lazy_property

from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage

from game.game_info import GENDER, ATTRIBUTES, RACE_TO_ENERGY_REGENERATION_TYPE

from game.balance.enums import RACE
from game.balance import constants as c, formulas as f, enums as e

from game import names

from game.artifacts.storage import artifacts_storage

from game.map.storage import map_info_storage

from game.text_generation import get_dictionary, get_text

from game.prototypes import TimePrototype

from game.heroes.bag import ARTIFACT_TYPE_TO_SLOT, SLOTS, SLOT_TO_ARTIFACT_TYPE
from game.heroes.statistics import HeroStatistics, MONEY_SOURCE
from game.heroes.preferences import HeroPreferences
from game.heroes.models import Hero
from game.heroes.habilities import AbilitiesPrototype, ABILITY_TYPE
from game.heroes.conf import heroes_settings
from game.heroes.exceptions import HeroException
from game.heroes.logic import ValuesDict
from game.heroes.pvp import PvPData
from game.heroes.messages import MessagesContainer
from game.heroes.places_help_statistics import PlacesHelpStatistics
from game.heroes.actions import ActionsContainer


class HeroPrototype(BasePrototype):
    _model_class = Hero
    _readonly = ('id', 'account_id', 'created_at_turn', 'name', 'experience', 'money', 'next_spending', 'energy', 'level')
    _bidirectional = ('is_alive',
                      'is_fast',
                      'gender',
                      'race',
                      'destiny_points_spend',
                      'last_energy_regeneration_at_turn',
                      'might',
                      'might_updated_time',
                      'ui_caching_started_at',
                      'active_state_end_at',
                      'premium_state_end_at')
    _get_by = ('id', 'account_id')

    def __init__(self, **kwargs):
        super(HeroPrototype, self).__init__(**kwargs)
        self.name_updated = False

    @property
    def is_premium(self):
        return self.premium_state_end_at > datetime.datetime.now()

    @property
    def is_active(self):
        return self.active_state_end_at > datetime.datetime.now()

    @property
    def birthday(self): return TimePrototype(self.created_at_turn).game_time

    @property
    def age(self):
        return TimePrototype(TimePrototype.get_current_turn_number() - self.created_at_turn).game_time

    @property
    def is_ui_caching_required(self):
        return (datetime.datetime.now() - self._model.ui_caching_started_at).seconds < heroes_settings.UI_CACHING_TIME

    ###########################################
    # Base attributes
    ###########################################

    @property
    def gender_verbose(self): return GENDER._ID_TO_TEXT[self.gender]

    @property
    def power(self): return f.clean_power_to_lvl(self.level) + self.equipment.get_power()

    @property
    def basic_damage(self): return f.damage_from_power(self.power) * self.damage_modifier

    @property
    def race_verbose(self): return RACE._ID_TO_TEXT[self.race]

    def add_experience(self, value):
        self._model.experience += self.abilities.modify_attribute(ATTRIBUTES.EXPERIENCE, value * self.experience_modifier)
        while f.exp_on_lvl(self.level) <= self._model.experience:
            self._model.experience -= f.exp_on_lvl(self.level)
            self._model.level += 1
            self.add_message('hero_common_level_up', hero=self, level=self.level)

    @property
    def max_ability_points_number(self):
        return f.max_ability_points_number(self.level)

    @property
    def current_ability_points_number(self):
        return sum(ability.level for ability in self.abilities.abilities.values())

    @property
    def can_choose_new_ability(self):
        return self.current_ability_points_number < self.max_ability_points_number

    @property
    def next_battle_ability_point_lvl(self):
        delta = self.level % 6
        return {0: 1,
                1: 2,
                2: 1,
                3: 4,
                4: 3,
                5: 2}[delta] + self.level

    @property
    def next_nonbattle_ability_point_lvl(self):
        delta = self.level % 6
        return {0: 5,
                1: 4,
                2: 3,
                3: 2,
                4: 1,
                5: 6}[delta] + self.level

    def get_health(self): return self._model.health
    def set_health(self, value): self._model.health = int(value)
    health = property(get_health, set_health)

    @property
    def health_percents(self): return float(self.health) / self.max_health

    def change_money(self, source, value):
        value = int(round(value))
        self.statistics.change_money(source, abs(value))
        self._model.money += value

    @property
    def abilities(self):
        if not hasattr(self, '_abilities'):
            if not self._model.abilities:
                # TODO: for migration to new ability representation
                self._abilities = AbilitiesPrototype.create()
            else:
                self._abilities = AbilitiesPrototype.deserialize(s11n.from_json(self._model.abilities))
        return self._abilities


    @property
    def next_ability_type(self):
        return {1: ABILITY_TYPE.BATTLE,
                2: ABILITY_TYPE.BATTLE,
                0: ABILITY_TYPE.NONBATTLE}[self.current_ability_points_number % 3]

    @property
    def ability_types_limitations(self):
        return {ABILITY_TYPE.BATTLE: (c.ABILITIES_ACTIVE_MAXIMUM, c.ABILITIES_PASSIVE_MAXIMUM),
                ABILITY_TYPE.NONBATTLE: (c.ABILITIES_NONBATTLE_MAXUMUM, c.ABILITIES_NONBATTLE_MAXUMUM)}[self.next_ability_type]

    def get_abilities_for_choose(self):

        random_state = random.getstate()
        random.seed(self.id + self.destiny_points_spend)

        max_abilities = self.ability_types_limitations

        candidates = self.abilities.get_candidates(ability_type=self.next_ability_type,
                                                   max_active_abilities=max_abilities[0],
                                                   max_passive_abilities=max_abilities[1])


        abilities = self.abilities.get_for_choose(candidates,
                                                  max_old_abilities_for_choose=c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM,
                                                  max_abilities_for_choose=c.ABILITIES_FOR_CHOOSE_MAXIMUM)

        random.setstate(random_state)

        return abilities


    @lazy_property
    def places_history(self): return PlacesHelpStatistics.deserialize(s11n.from_json(self._model.places_history))

    @lazy_property
    def quests_history(self): return ValuesDict.deserialize(s11n.from_json(self._model.quests_history))

    def get_special_quests(self):
        from game.quests.quests_builders import Hunt
        from game.quests.quests_builders import Hometown
        from game.quests.quests_builders import HelpFriend
        from game.quests.quests_builders import InterfereEnemy
        from game.quests.quests_builders import SearchSmith

        allowed_quests = []

        if self.preferences.mob is not None:
            allowed_quests.append(Hunt.type())
        if self.preferences.place_id is not None:
            allowed_quests.append(Hometown.type())
        if self.preferences.friend_id is not None:
            allowed_quests.append(HelpFriend.type())
        if self.preferences.enemy_id is not None:
            allowed_quests.append(InterfereEnemy.type())
        if self.preferences.equipment_slot is not None:
            equipped_artifact = self.equipment.get(self.preferences.equipment_slot)
            equipped_power = equipped_artifact.power if equipped_artifact else -1
            min_power, max_power = f.power_to_artifact_interval(self.level)
            if equipped_power <= max_power:
                allowed_quests.append(SearchSmith.type())

        return allowed_quests

    @property
    def bag(self):
        if not hasattr(self, '_bag'):
            from .bag import Bag
            self._bag = Bag()
            self._bag.deserialize(s11n.from_json(self._model.bag))
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


    def buy_artifact(self, better=False, with_preferences=True, equip=True):
        artifacts_list = None
        if self.preferences.equipment_slot is not None:
            if with_preferences:
                artifact_types = [SLOT_TO_ARTIFACT_TYPE[self.preferences.equipment_slot]]
            else:
                artifact_types = set(SLOT_TO_ARTIFACT_TYPE.values())
                artifact_types -= set([SLOT_TO_ARTIFACT_TYPE[self.preferences.equipment_slot]])

            artifacts_list = artifacts_storage.artifacts_for_type(artifact_types)

        if not artifacts_list:
            # if hero has not preferences or can not get any item for preferences slot
            artifacts_list = artifacts_storage.artifacts

        artifact = artifacts_storage.generate_artifact_from_list(artifacts_list, self.level)

        if artifact is None:
            return None, None, None

        self.bag.put_artifact(artifact)

        if not equip:
            return artifact, None, None

        slot = ARTIFACT_TYPE_TO_SLOT[artifact.type.value]
        unequipped = self.equipment.get(slot)

        if better and unequipped is not None and artifact.power < unequipped.power:
            artifact.power = unequipped.power + 1

        min_power, max_power = f.power_to_artifact_interval(self.level)
        artifact.power = min(artifact.power, max_power)

        self.change_equipment(slot, unequipped, artifact)

        self.statistics.change_artifacts_had(1)

        sell_price = None

        if unequipped is not None:
            sell_price = self.sell_artifact(unequipped)

        return artifact, unequipped, sell_price

    def sell_artifact(self, artifact):
        sell_price = artifact.get_sell_price()

        sell_price = self.modify_sell_price(sell_price)

        if artifact.is_useless:
            money_source = MONEY_SOURCE.EARNED_FROM_LOOT
        else:
            money_source = MONEY_SOURCE.EARNED_FROM_ARTIFACTS

        self.change_money(money_source, sell_price)
        self.bag.pop_artifact(artifact)

        return sell_price

    def modify_sell_price(self, price):
        price = self.abilities.update_sell_price(self, price)

        if self.position.place and self.position.place.modifier:
            price = self.position.place.modifier.modify_sell_price(price)

        return int(round(price))

    def modify_buy_price(self, price):
        price = self.abilities.update_buy_price(self, price)

        if self.position.place and self.position.place.modifier:
            price = self.position.place.modifier.modify_buy_price(price)

        return int(round(price))


    def sharp_artifact(self):
        choices = copy.copy(SLOTS._ALL)
        random.shuffle(choices)

        if self.preferences.equipment_slot is not None:
            choices.insert(0, self.preferences.equipment_slot)

        min_power, max_power = f.power_to_artifact_interval(self.level)

        for slot in choices:
            artifact = self.equipment.get(slot)
            if artifact is not None and artifact.power < max_power:
                artifact.power += 1
                self.equipment.updated = True
                return artifact

        # if all artifacts are on maximum level
        random.shuffle(choices)
        for slot in choices:
            artifact = self.equipment.get(slot)
            if artifact is not None:
                artifact.power += 1
                self.equipment.updated = True
                return artifact


    def get_equip_canditates(self):

        equipped_slot = None
        equipped = None
        unequipped = None

        for uuid, artifact in self.bag.items():
            if not artifact.can_be_equipped:
                continue

            slot = ARTIFACT_TYPE_TO_SLOT[artifact.type.value]

            equipped_artifact = self.equipment.get(slot)

            if equipped_artifact is None:
                equipped_slot = slot
                equipped = artifact
                break

            if equipped_artifact.power < artifact.power:
                equipped = artifact
                unequipped = equipped_artifact
                equipped_slot = slot
                break

        return equipped_slot, unequipped, equipped


    def change_equipment(self, slot, unequipped, equipped):
        if unequipped:
            self.equipment.unequip(slot)
            self.bag.put_artifact(unequipped)

        if equipped:
            self.bag.pop_artifact(equipped)
            self.equipment.equip(slot, equipped)

    def can_get_artifact_for_quest(self):
        return self.abilities.can_get_artifact_for_quest(self)

    def can_buy_better_artifact(self):
        if self.abilities.can_buy_better_artifact(self):
            return True

        if self.position.place and self.position.place.modifier and self.position.place.modifier.can_buy_better_artifact():
            return True

        return False

    @property
    def equipment(self):
        if not hasattr(self, '_equipment'):
            from .bag import Equipment
            self._equipment = Equipment()
            self._equipment.deserialize(s11n.from_json(self._model.equipment))
        return self._equipment

    @property
    def is_name_changed(self):
        return bool(self._model.name_forms)

    def get_normalized_name(self):
        if not hasattr(self, '_normalized_name'):
            if not self.is_name_changed:
                if self.gender == GENDER.MASCULINE:
                    self._normalized_name = get_dictionary().get_word(u'герой')
                elif self.gender == GENDER.FEMININE:
                    self._normalized_name = get_dictionary().get_word(u'героиня')
            else:
                self._normalized_name = Noun.deserialize(s11n.from_json(self._model.name_forms))
        return self._normalized_name
    def set_normalized_name(self, word):
        self._normalized_name = word
        self._model.name = word.normalized
        self._model.name_forms = s11n.to_json(word.serialize()) # need to correct work of is_name_changed
        self.name_updated = True

    normalized_name = property(get_normalized_name, set_normalized_name)

    def switch_spending(self):
        priorities = self.abilities.update_items_of_expenditure_priorities(self, c.ITEMS_OF_EXPENDITURE_PRIORITY)
        self._model.next_spending = random_value_by_priority(list(priorities.items()))

    @property
    def energy_maximum(self): return c.ANGEL_ENERGY_MAX

    def change_energy(self, value):
        old_energy = self._model.energy

        self._model.energy += value
        if self._model.energy < 0:
            self._model.energy = 0
        elif self._model.energy > self.energy_maximum:
            self._model.energy = self.energy_maximum

        if self._model.energy != old_energy:
            self.updated = True

        return self._model.energy - old_energy

    @property
    def might_crit_chance(self): return self.abilities.modify_attribute(ATTRIBUTES.MIGHT_CRIT_CHANCE, f.might_crit_chance(self.might))

    @property
    def might_pvp_effectiveness_bonus(self): return f.might_pvp_effectiveness_bonus(self.might)

    def on_highlevel_data_updated(self):
        if self.preferences.friend_id is not None and self.preferences.friend.out_game:
            self.preferences.friend_id = None
            self.preferences.friend_changed_at = datetime.datetime(2000, 1, 1)

        if self.preferences.enemy_id is not None and self.preferences.enemy.out_game:
            self.preferences.enemy_id = None
            self.preferences.enemy_changed_at = datetime.datetime(2000, 1, 1)

    def modify_person_power(self, person, power):
        if person.id in (self.preferences.friend_id, self.preferences.enemy_id):
            power *= c.HERO_POWER_PREFERENCE_MULTIPLIER
        if person.place_id == self.preferences.place_id:
            power *= c.HERO_POWER_PREFERENCE_MULTIPLIER
        return int(power)

    ###########################################
    # Secondary attributes
    ###########################################

    @property
    def damage_modifier(self): return self.abilities.modify_attribute(ATTRIBUTES.DAMAGE, 1)

    @property
    def move_speed(self): return self.abilities.modify_attribute(ATTRIBUTES.SPEED, 0.3)

    @property
    def initiative(self): return self.abilities.modify_attribute(ATTRIBUTES.INITIATIVE, 1)

    @property
    def max_health(self): return int(f.hp_on_lvl(self.level) * self.abilities.modify_attribute(ATTRIBUTES.HEALTH, 1))

    @property
    def max_bag_size(self): return c.MAX_BAG_SIZE

    @property
    def experience_modifier(self):
        if self.is_premium or self.is_active:
            return 1.0
        return 1.0 * c.EXP_PENALTY_MULTIPLIER

    ###########################################
    # Permissions
    ###########################################

    @property
    def can_change_persons_power(self): return self.is_premium

    @property
    def can_participate_in_pvp(self): return not self.is_fast

    @property
    def can_repair_building(self):  return self.is_premium

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

    @property
    def need_regenerate_energy(self):
        return TimePrototype.get_current_turn_number() > self.last_energy_regeneration_at_turn + f.angel_energy_regeneration_delay(self.preferences.energy_regeneration_type)

    @lazy_property
    def position(self): return HeroPositionPrototype(hero_model=self._model)

    @lazy_property
    def statistics(self): return HeroStatistics(hero_model=self._model)

    @lazy_property
    def preferences(self): return HeroPreferences(hero_model=self._model)

    @lazy_property
    def actions(self): return ActionsContainer.deserialize(s11n.from_json(self._model.actions))

    @lazy_property
    def pvp(self): return PvPData.deserialize(s11n.from_json(self._model.pvp))

    @lazy_property
    def messages(self): return MessagesContainer.deserialize(s11n.from_json(self._model.messages))

    @lazy_property
    def diary(self): return MessagesContainer.deserialize(s11n.from_json(self._model.diary))

    def push_message(self, msg, important=False):
        self.messages.push_message(msg)

        if important:
            self.diary.push_message(msg)

    def add_message(self, type_, important=False, turn_delta=0, **kwargs):
        msg = get_text('hero:add_message', type_, kwargs)
        if msg is None: return
        self.push_message(MessagesContainer._prepair_message(msg, turn_delta=turn_delta), important=important)


    def heal(self, delta):
        if delta < 0:
            raise HeroException('can not heal hero for value less then 0')
        old_health = self.health
        self.health = int(min(self.health + delta, self.max_health))
        return self.health - old_health

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        self._model.delete()

    def save(self):

        if self.bag.updated:
            self._model.bag = s11n.to_json(self.bag.serialize())
            self.bag.updated = False

        if self.equipment.updated:
            self._model.equipment = s11n.to_json(self.equipment.serialize())
            self._model.raw_power = self.power
            self.equipment.updated = False

        if self.abilities.updated:
            self._model.abilities = s11n.to_json(self.abilities.serialize())
            self.abilities.updated = False

        if self.places_history.updated:
            self._model.places_history = s11n.to_json(self.places_history.serialize())
            self.places_history.updated = False

        if self.quests_history.updated:
            self._model.quests_history = s11n.to_json(self.quests_history.serialize())
            self.quests_history.updated = False

        if self.messages.updated:
            self._model.messages = s11n.to_json(self.messages.serialize())
            self.messages.updated = False

        if self.diary.updated:
            self._model.diary = s11n.to_json(self.diary.serialize())
            self.diary.updated = False

        if self.actions.updated:
            self._model.actions = s11n.to_json(self.actions.serialize())
            self.actions.updated = False

        if self.name_updated:
            self._model.name_forms = s11n.to_json(self.normalized_name.serialize())
            self.name_updated = False

        if self.pvp.updated:
            self._model.pvp = s11n.to_json(self.pvp.serialize())
            self.pvp.updated = False

        database.raw_save(self._model)

    @classmethod
    def get_friendly_heroes(self, person):
        return [HeroPrototype(model=record) for record in Hero.objects.filter(pref_friend_id=person.id, active_state_end_at__gte=datetime.datetime.now())]

    @classmethod
    def get_enemy_heroes(self, person):
        return [HeroPrototype(model=record) for record in Hero.objects.filter(pref_enemy_id=person.id, active_state_end_at__gte=datetime.datetime.now())]

    @classmethod
    def get_place_heroes(self, place):
        return [HeroPrototype(model=record) for record in Hero.objects.filter(pref_place_id=place.id, active_state_end_at__gte=datetime.datetime.now())]

    def __eq__(self, other):

        return (self.id == other.id and
                self.is_alive == other.is_alive and
                self.is_fast == other.is_fast and
                self.name == other.name and
                self.gender == other.gender and
                self.race == other.race and
                self.level == other.level and
                self.actions == other.actions and
                self.experience == other.experience and
                self.health == other.health and
                self.money == other.money and
                self.abilities == other.abilities and
                self.bag == other.bag and
                self.equipment == other.equipment and
                self.next_spending == other.next_spending and
                self.position == other.position and
                self.statistics == other.statistics and
                self.messages == other.messages and
                self.diary == other.diary)

    def ui_info(self, for_last_turn=False, quests_info=False):
        from game.quests.prototypes import QuestPrototype

        quest_items_count, loot_items_count = self.bag.occupation

        quests = None
        if quests_info:
            quest = QuestPrototype.get_for_hero(self.id)
            quests = quest.ui_info(self) if quest else {}

        return {'id': self.id,
                'messages': self.messages.ui_info(),
                'diary': self.diary.ui_info(with_date=True),
                'position': self.position.ui_info(),
                'alive': self.is_alive,
                'bag': self.bag.ui_info(),
                'equipment': self.equipment.ui_info(),
                'money': self.money,
                'might': self.might,
                'might_crit_chance': '%.2f' % (self.might_crit_chance*100),
                'might_pvp_effectiveness_bonus': '%.2f' % (self.might_pvp_effectiveness_bonus*100),
                'can_participate_in_pvp': self.can_participate_in_pvp,
                'can_repair_building': self.can_repair_building,
                'energy': { 'max': self.energy_maximum,
                            'value': self.energy },
                'next_spending': { e.ITEMS_OF_EXPENDITURE.INSTANT_HEAL: 'heal',
                                   e.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT: 'artifact',
                                   e.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT: 'sharpening',
                                   e.ITEMS_OF_EXPENDITURE.USELESS: 'useless',
                                   e.ITEMS_OF_EXPENDITURE.IMPACT: 'impact'}[self.next_spending],
                'action': self.actions.current_action.ui_info(),
                'pvp': self.pvp.ui_info() if not for_last_turn else self.pvp.turn_ui_info(),
                'base': { 'name': self.name,
                          'level': self.level,
                          'destiny_points': self.max_ability_points_number - self.current_ability_points_number,
                          'health': self.health,
                          'max_health': self.max_health,
                          'experience': self.experience * c.EXP_MULTIPLICATOR,
                          'experience_to_level': f.exp_on_lvl(self.level) * c.EXP_MULTIPLICATOR,
                          'gender': self.gender,
                          'race': self.race },
                'secondary': { 'power': math.floor(self.power),
                               'move_speed': self.move_speed,
                               'initiative': self.initiative,
                               'max_bag_size': self.max_bag_size,
                               'loot_items_count': loot_items_count,
                               'quest_items_count': quest_items_count},
                'quests': quests
                }

    def ui_info_for_cache(self):
        return self.ui_info(for_last_turn=False, quests_info=True)


    @classmethod
    def cached_ui_info_key_for_hero(cls, account_id):
        return heroes_settings.UI_CACHING_KEY % account_id

    @property
    def cached_ui_info_key(self):
        return self.cached_ui_info_key_for_hero(self.account_id)

    @classmethod
    def cached_ui_info_for_hero(cls, account_id):
        from game.workers.environment import workers_environment as game_workers_environment

        data = cache.get(cls.cached_ui_info_key_for_hero(account_id))

        if data is None:
            hero = cls.get_by_account_id(account_id)
            data = hero.ui_info_for_cache()

            if not hero.is_ui_caching_required:
                # in other case it is probably some delay in turn processing and we shouldn't spam unnecessary messages
                game_workers_environment.supervisor.cmd_start_hero_caching(hero.account_id, hero.id)

        return data

    @classmethod
    def create(cls, account, bundle):

        from game.abilities.prototypes import AbilityPrototype
        from game.actions.prototypes import ActionIdlenessPrototype
        from game.logic_storage import LogicStorage

        start_place = places_storage.random_place()

        race = random.choice(RACE._ALL)

        gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

        current_turn_number = TimePrototype.get_current_turn_number()

        energy_regeneration_type = RACE_TO_ENERGY_REGENERATION_TYPE[race]

        name = names.generator.get_name(race, gender)

        messages = MessagesContainer()
        messages.push_message(messages._prepair_message(u'«Тучи сгущаются (и как быстро!), к непогоде»', turn_delta=-7))
        messages.push_message(messages._prepair_message(u'«Аааааа, повсюду молнии, спрячусь ка я под этим большим дубом».', turn_delta=-6))
        messages.push_message(messages._prepair_message(u'Бабах!!!', turn_delta=-5))
        messages.push_message(messages._prepair_message(u'«Темно, страшно, кажется, я в коридоре»…', turn_delta=-4))
        messages.push_message(messages._prepair_message(u'«Свет! Надо идти на свет»!', turn_delta=-3))
        messages.push_message(messages._prepair_message(u'«Свет сказал, что избрал меня для великих дел, взял кровь из пальца и поставил ей крестик в каком-то пергаменте».', turn_delta=-2))
        messages.push_message(messages._prepair_message(u'«Приказано идти обратно и геройствовать, как именно геройствовать — не уточняется».', turn_delta=-1))
        messages.push_message(messages._prepair_message(u'«Эх, опять в этом мире, в том было хотя бы чисто и сухо. Голова болит. Палец болит. Тянет на подвиги».', turn_delta=-0))

        diary = MessagesContainer()
        diary.push_message(diary._prepair_message(u'«Вот же ж угораздило. У всех ангелы-хранители нормальные, сидят себе и попаданию подопечных в загробный мир не мешают. А у моего, значит, шило в заднице! Где ты был, когда я лотерейные билеты покупал?! Молнию отвести он значит не может, а воскресить — запросто. Как же всё болит, кажется теперь у меня две печёнки (это, конечно, тебе спасибо, всегда пригодится). Ну ничего, рано или поздно я к твоему начальству попаду и там уж всё расскажу! А пока буду записывать в свой дневник».'))

        hero = Hero.objects.create(created_at_turn=current_turn_number,
                                   active_state_end_at=account.active_end_at,
                                   premium_state_end_at=account.premium_end_at,
                                   account=account._model,
                                   gender=gender,
                                   race=race,
                                   is_fast=account.is_fast,
                                   pref_energy_regeneration_type=energy_regeneration_type,
                                   abilities=s11n.to_json(AbilitiesPrototype.create().serialize()),
                                   messages=s11n.to_json(messages.serialize()),
                                   diary=s11n.to_json(diary.serialize()),
                                   name=name,
                                   health=f.hp_on_lvl(1),
                                   energy=c.ANGEL_ENERGY_MAX,
                                   pos_place = start_place._model)

        hero = cls(model=hero)

        AbilityPrototype.create(hero)

        storage = LogicStorage() # tmp storage for creating Idleness action

        storage.add_hero(hero)

        ActionIdlenessPrototype.create(parent=None, _bundle_id=bundle.id, hero=hero, _storage=storage)

        return hero

    def update_with_account_data(self, is_fast, premium_end_at, active_end_at):
        self.is_fast = is_fast
        self.active_state_end_at = active_end_at
        self.premium_state_end_at = premium_end_at

    def cmd_update_with_account_data(self, account):
        from game.workers.environment import workers_environment as game_workers_environment

        game_workers_environment.supervisor.cmd_update_hero_with_account_data(account.id,
                                                                              self.id,
                                                                              is_fast=account.is_fast,
                                                                              premium_end_at=account.premium_end_at,
                                                                              active_end_at=account.active_end_at)


    ###########################################
    # Game operations
    ###########################################

    def kill(self):
        self.health = 1
        self.is_alive = False

    def resurrect(self):
        self.health = self.max_health
        self.is_alive = True



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
        self.hero_model.pos_place = place._model

    @property
    def road_id(self): return self.hero_model.pos_road_id

    @property
    def road(self): return roads_storage.get(self.hero_model.pos_road_id)

    def set_road(self, road, percents=0, invert=False):
        self._reset_position()
        self.hero_model.pos_road = road._model
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
        map_info = map_info_storage.item
        x, y = self.cell_coordinates
        return map_info.terrain[y][x]

    def get_dominant_place(self):
        if self.place:
            return self.place
        else:
            return map_info_storage.item.get_dominant_place(*self.cell_coordinates)

    def is_battle_start_needed(self):
        battles_per_turn = c.BATTLES_PER_TURN

        dominant_place = self.get_dominant_place()

        if dominant_place and dominant_place.modifier:
            battles_per_turn = dominant_place.modifier.modify_battles_per_turn(battles_per_turn)

        return random.uniform(0, 1) <= battles_per_turn

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        return {'place_id': self.place.id if self.place else None,
                'road_id': self.road.id if self.road else None,
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
