# coding: utf-8
import math
import datetime
import time
import random

from textgen.words import Noun

from dext.utils import s11n, database, cache

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.logic import random_value_by_priority
from the_tale.common.utils.decorators import lazy_property

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage

from the_tale.game.map.storage import map_info_storage

from the_tale.game.balance import constants as c, formulas as f

from the_tale.game import names

from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.text_generation import get_dictionary, get_text

from the_tale.game.prototypes import TimePrototype

from the_tale.game.actions.container import ActionsContainer
from the_tale.game.quests.container import QuestsContainer

from the_tale.game.heroes.statistics import HeroStatistics
from the_tale.game.heroes.models import Hero, HeroPreferences
from the_tale.game.heroes.habilities import AbilitiesPrototype
from the_tale.game.heroes.conf import heroes_settings
from the_tale.game.heroes import exceptions
from the_tale.game.heroes.pvp import PvPData
from the_tale.game.heroes.messages import MessagesContainer
from the_tale.game.heroes.places_help_statistics import PlacesHelpStatistics
from the_tale.game.heroes import relations
from the_tale.game.heroes import habits
from the_tale.game.heroes import logic_accessors
from the_tale.game.heroes import bag



class HeroPrototype(BasePrototype, logic_accessors.LogicAccessorsMixin):
    _model_class = Hero
    _readonly = ('id', 'account_id', 'created_at_turn', 'name', 'experience', 'money', 'next_spending', 'energy', 'level', 'saved_at_turn', 'saved_at', 'is_bot')
    _bidirectional = ('is_alive',
                      'is_fast',
                      'gender',
                      'race',
                      'last_energy_regeneration_at_turn',
                      'might',
                      'might_updated_time',
                      'ui_caching_started_at',
                      'active_state_end_at',
                      'premium_state_end_at',
                      'ban_state_end_at',
                      'energy_bonus',
                      'last_rare_operation_at_turn',
                      'health')
    _get_by = ('id', 'account_id')
    _serialization_proxies = (('quests', QuestsContainer, heroes_settings.UNLOAD_TIMEOUT),
                              ('places_history', PlacesHelpStatistics, heroes_settings.UNLOAD_TIMEOUT),
                              ('pvp', PvPData, heroes_settings.UNLOAD_TIMEOUT),
                              ('diary', MessagesContainer, heroes_settings.UNLOAD_TIMEOUT),
                              ('abilities', AbilitiesPrototype, None),
                              ('bag', bag.Bag, None),
                              ('equipment', bag.Equipment, None))

    @classmethod
    def live_query(cls): return cls._model_class.objects.filter(is_fast=False, is_bot=False)

    @property
    def is_premium(self):
        return self.premium_state_end_at > datetime.datetime.now()

    @property
    def is_banned(self):
        return self.ban_state_end_at > datetime.datetime.now()

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
        return (datetime.datetime.now() - self._model.ui_caching_started_at).total_seconds() < heroes_settings.UI_CACHING_TIME

    @classmethod
    def is_ui_continue_caching_required(self, ui_caching_started_at):
        return ui_caching_started_at + heroes_settings.UI_CACHING_TIME - heroes_settings.UI_CACHING_CONTINUE_TIME < time.time()

    ###########################################
    # Base attributes
    ###########################################

    mob_type = None

    @property
    def gender_verbose(self): return self.gender.text

    @property
    def power(self): return f.clean_power_to_lvl(self.level) + self.equipment.get_power()

    @property
    def basic_damage(self): return f.damage_from_power(self.power) * self.damage_modifier

    @property
    def race_verbose(self): return self.race.text

    def increment_level(self):
        self._model.level += 1
        self.add_message('hero_common_journal_level_up', hero=self, level=self.level)

    def add_experience(self, value):
        real_experience = int(value * self.experience_modifier)
        self._model.experience += real_experience

        while f.exp_on_lvl(self.level) <= self._model.experience:
            self._model.experience -= f.exp_on_lvl(self.level)
            self.increment_level()

        return real_experience

    def add_energy_bonus(self, energy):
        self.energy_bonus += energy

    @property
    def health_percents(self): return float(self.health) / self.max_health

    def change_money(self, source, value):
        value = int(round(value))
        self.statistics.change_money(source, abs(value))
        self._model.money += value

    def get_quests(self):
        # always check hero position to prevent «bad» quests generation
        from the_tale.game.quests.relations import QUESTS

        quests = [quest for quest in QUESTS.records if quest.quest_type.is_NORMAL]

        if self.preferences.mob is not None:
            quests.append(QUESTS.HUNT)
        if self.preferences.place is not None and (self.position.place is None or self.preferences.place.id != self.position.place.id):
            quests.append(QUESTS.HOMETOWN)
        if self.preferences.friend is not None and (self.position.place is None or self.preferences.friend.place.id != self.position.place.id):
            quests.append(QUESTS.HELP_FRIEND)
        if self.preferences.enemy is not None and (self.position.place is None or self.preferences.enemy.place.id != self.position.place.id):
            quests.append(QUESTS.INTERFERE_ENEMY)
        if self.preferences.equipment_slot is not None:
            equipped_artifact = self.equipment.get(self.preferences.equipment_slot)
            equipped_power = equipped_artifact.power if equipped_artifact else -1
            min_power, max_power = f.power_to_artifact_interval(self.level) # pylint: disable=W0612
            if equipped_power <= max_power:
                quests.append(QUESTS.SEARCH_SMITH)

        if any(place.modifier and place.modifier.TYPE.is_HOLY_CITY for place in places_storage.all()):
            if self.position.place is None or self.position.place.modifier is None or not self.position.place.modifier.TYPE.is_HOLY_CITY:
                quests.append(QUESTS.PILGRIMAGE)

        return [(quest, self.modify_quest_priority(quest)) for quest in quests]

    @classmethod
    def get_minimum_created_time_of_active_quests(cls):
        from django.db.models import Min
        created_at = cls._model_class.objects.all().aggregate(Min('quest_created_time'))['quest_created_time__min']
        return created_at if created_at is not None else datetime.datetime.now()

    def put_loot(self, artifact):
        if not self.bag_is_full:
            self.bag.put_artifact(artifact)
            return artifact.bag_uuid

    def pop_loot(self, artifact):
        self.bag.pop_artifact(artifact)

    def buy_artifact_choices(self, equip, with_prefered_slot):

        allowed_slots = list(relations.EQUIPMENT_SLOT.records)

        if self.preferences.favorite_item and equip:
            allowed_slots.remove(self.preferences.favorite_item)

        slot_choices = allowed_slots

        if with_prefered_slot and self.preferences.equipment_slot is not None and self.preferences.equipment_slot in allowed_slots:
            slot_choices = [self.preferences.equipment_slot]

        artifacts_choices = artifacts_storage.artifacts_for_type([slot.artifact_type for slot in slot_choices])

        if not artifacts_choices:
            artifacts_choices = artifacts_storage.artifacts_for_type([slot.artifact_type for slot in allowed_slots])

        return artifacts_choices

    def buy_artifact(self, better, with_prefered_slot, equip):

        artifact_choices = self.buy_artifact_choices(equip=equip, with_prefered_slot=with_prefered_slot)

        artifact = artifacts_storage.generate_artifact_from_list(artifact_choices, self.level)

        if artifact is None:
            return None, None, None

        if artifact.type.equipment_slot == self.preferences.equipment_slot:
            better = True

        self.bag.put_artifact(artifact)
        self.statistics.change_artifacts_had(1)

        if not equip:
            return artifact, None, None

        slot = artifact.type.equipment_slot
        unequipped = self.equipment.get(slot)

        if better and unequipped is not None and artifact.power < unequipped.power:
            artifact.power = unequipped.power + 1

        min_power, max_power = f.power_to_artifact_interval(self.level) # pylint: disable=W0612
        artifact.power = min(artifact.power, max_power)

        self.change_equipment(slot, unequipped, artifact)

        sell_price = None

        if unequipped is not None:
            sell_price = self.sell_artifact(unequipped)

        return artifact, unequipped, sell_price

    def sell_artifact(self, artifact):
        sell_price = artifact.get_sell_price()

        sell_price = self.modify_sell_price(sell_price)

        if artifact.is_useless:
            money_source = relations.MONEY_SOURCE.EARNED_FROM_LOOT
        else:
            money_source = relations.MONEY_SOURCE.EARNED_FROM_ARTIFACTS

        self.change_money(money_source, sell_price)
        self.bag.pop_artifact(artifact)

        return sell_price

    def sharp_artifact(self):
        choices = list(relations.EQUIPMENT_SLOT.records)
        random.shuffle(choices)

        if self.preferences.equipment_slot is not None:
            choices.insert(0, self.preferences.equipment_slot)

        min_power, max_power = f.power_to_artifact_interval(self.level) # pylint: disable=W0612

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

        for artifact in self.bag.values():
            if not artifact.can_be_equipped:
                continue

            slot = artifact.type.equipment_slot

            if self.preferences.favorite_item == slot:
                continue

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

    def equip_from_bag(self):
        slot, unequipped, equipped = self.get_equip_canditates()
        self.change_equipment(slot, unequipped, equipped)
        return slot, unequipped, equipped

    def change_equipment(self, slot, unequipped, equipped):
        if unequipped:
            self.equipment.unequip(slot)
            self.bag.put_artifact(unequipped)

        if equipped:
            self.bag.pop_artifact(equipped)
            self.equipment.equip(slot, equipped)

    @property
    def is_name_changed(self):
        return bool(self._model.name_forms)

    def get_normalized_name(self):
        if not hasattr(self, '_normalized_name'):
            if not self.is_name_changed:
                if self.gender.is_MASCULINE:
                    self._normalized_name = get_dictionary().get_word(u'герой')
                elif self.gender.is_FEMININE:
                    self._normalized_name = get_dictionary().get_word(u'героиня')
            else:
                self._normalized_name = Noun.deserialize(s11n.from_json(self._model.name_forms))
        return self._normalized_name
    def set_normalized_name(self, word):
        self._normalized_name = word
        self._model.name = word.normalized
        self._model.name_forms = s11n.to_json(word.serialize()) # need to correct work of is_name_changed

    normalized_name = property(get_normalized_name, set_normalized_name)

    def switch_spending(self):
        self._model.next_spending = random_value_by_priority(list(self.spending_priorities().items()))

    @property
    def energy_full(self):
        return self.energy + self.energy_bonus

    def change_energy(self, value):
        old_energy = self.energy_full

        self._model.energy += value

        if self._model.energy < 0:
            self._model.energy_bonus += self._model.energy
            self._model.energy = 0

        elif self._model.energy > self.energy_maximum:
            self._model.energy = self.energy_maximum

        if self._model.energy_bonus < 0:
            self._model.energy_bonus = 0

        return self.energy_full - old_energy

    def change_habits(self, habit_type, habit_value):

        if habit_type == self.habit_honor.TYPE:
            self.habit_honor.change(habit_value)

        if habit_type == self.habit_peacefulness.TYPE:
            self.habit_peacefulness.change(habit_value)


    @property
    def might_pvp_effectiveness_bonus(self): return f.might_pvp_effectiveness_bonus(self.might)

    def on_highlevel_data_updated(self):
        if self.preferences.friend is not None and self.preferences.friend.out_game:
            self.preferences.reset_friend()

        if self.preferences.enemy is not None and self.preferences.enemy.out_game:
            self.preferences.reset_enemy()

    def modify_power(self, power, person=None, place=None):

        if person and self.preferences.friend and person.id == self.preferences.friend.id:
            power *= self.friend_power_modifier

        if person and self.preferences.enemy and person.id == self.preferences.enemy.id:
            power *= self.enemy_power_modifier

        positive_bonus = 0.0
        negative_bonus = 0.0

        if ((self.preferences.place and place and place.id == self.preferences.place.id) or
            (self.preferences.friend and person and person.id == self.preferences.friend.id) or
            (self.preferences.enemy and person and person.id == self.preferences.enemy.id)):
            if power > 0:
                positive_bonus = c.HERO_POWER_BONUS
            elif power < 0:
                negative_bonus = c.HERO_POWER_BONUS

        return (int(power * self.person_power_modifier),
                positive_bonus * self.person_power_modifier,
                negative_bonus * self.person_power_modifier)

    @lazy_property
    def habit_honor(self): return habits.Honor(self, 'honor')

    @lazy_property
    def habit_peacefulness(self): return habits.Peacefulness(self, 'peacefulness')

    def update_habits(self, change_source, multuplier=1.0):

        if change_source.quest_default is False:
            multuplier *= self.habit_quest_active_multiplier

        if change_source.correlation_requirements is None:
            self.habit_honor.change(change_source.honor*multuplier)
            self.habit_peacefulness.change(change_source.peacefulness*multuplier)

        elif change_source.correlation_requirements:
            if self.habit_honor.raw_value * change_source.honor > 0:
                self.habit_honor.change(change_source.honor*multuplier)
            if self.habit_peacefulness.raw_value * change_source.peacefulness > 0:
                self.habit_peacefulness.change(change_source.peacefulness*multuplier)

        else:
            if self.habit_honor.raw_value * change_source.honor < 0:
                self.habit_honor.change(change_source.honor*multuplier)
            if self.habit_peacefulness.raw_value * change_source.peacefulness < 0:
                self.habit_peacefulness.change(change_source.peacefulness*multuplier)

    ###########################################
    # Permissions
    ###########################################

    @property
    def can_change_persons_power(self): return self.is_premium and not self.is_banned

    @property
    def can_participate_in_pvp(self): return not self.is_fast and not self.is_banned

    @property
    def can_repair_building(self):  return self.is_premium and not self.is_banned

    ###########################################
    # Needs attributes
    ###########################################

    @property
    def need_rest_in_settlement(self): return self.health < self.max_health * c.HEALTH_IN_SETTLEMENT_TO_START_HEAL_FRACTION * self.preferences.risk_level.health_percent_to_rest

    @property
    def need_rest_in_move(self): return self.health < self.max_health * c.HEALTH_IN_MOVE_TO_START_HEAL_FRACTION * self.preferences.risk_level.health_percent_to_rest

    @property
    def need_trade_in_town(self):
        return float(self.bag.occupation) / self.max_bag_size > c.BAG_SIZE_TO_SELL_LOOT_FRACTION

    @property
    def need_equipping_in_town(self):
        slot, unequipped, equipped = self.get_equip_canditates() # pylint: disable=W0612
        return equipped is not None

    @property
    def need_regenerate_energy(self):
        return TimePrototype.get_current_turn_number() > self.last_energy_regeneration_at_turn + f.angel_energy_regeneration_delay(self.preferences.energy_regeneration_type)

    @lazy_property
    def position(self): return HeroPositionPrototype(hero_model=self._model)

    @lazy_property
    def statistics(self): return HeroStatistics(hero=self)

    @lazy_property
    def preferences(self):
        from the_tale.game.heroes.preferences import HeroPreferences

        preferences = HeroPreferences.deserialize(hero_id=self.id, data=s11n.from_json(self._model.preferences))
        if preferences.energy_regeneration_type is None:
            preferences.set_energy_regeneration_type(self.race.energy_regeneration, change_time=datetime.datetime.fromtimestamp(0))
        if preferences.risk_level is None:
            preferences.set_risk_level(relations.RISK_LEVEL.NORMAL, change_time=datetime.datetime.fromtimestamp(0))
        return preferences

    def reset_preference(self, preference_type):
        if preference_type.is_ENERGY_REGENERATION_TYPE:
            self.preferences.set_energy_regeneration_type(self.race.energy_regeneration, change_time=datetime.datetime.fromtimestamp(0))
        elif preference_type.is_RISK_LEVEL:
            self.preferences.set_risk_level(relations.RISK_LEVEL.NORMAL, change_time=datetime.datetime.fromtimestamp(0))
        else:
            self.preferences._reset(preference_type)

    def reset_abilities(self):
        self.abilities.reset()

    def rechooce_abilities_choices(self):
        self.abilities.rechooce_choices()

    @lazy_property
    def actions(self): return ActionsContainer.deserialize(self, s11n.from_json(self._model.actions))

    @lazy_property
    def messages(self): return MessagesContainer.deserialize(self, s11n.from_json(self._model.messages))

    def push_message(self, msg, diary=False, journal=True):
        if journal:
            self.messages.push_message(msg)

        if diary:
            self.diary.push_message(msg)

    def add_message(self, type_, diary=False, journal=True, turn_delta=0, **kwargs):
        msg = get_text('hero:add_message', type_, kwargs)
        if msg is None: return
        self.push_message(MessagesContainer._prepair_message(msg, turn_delta=turn_delta), diary=diary, journal=journal)


    def heal(self, delta):
        if delta < 0:
            raise exceptions.HealHeroForNegativeValueError()
        old_health = self.health
        self.health = int(min(self.health + delta, self.max_health))
        return self.health - old_health

    def can_be_healed(self, strict=False):
        if strict:
            return self.is_alive and self.max_health > self.health

        return self.is_alive and (c.ANGEL_HELP_HEAL_IF_LOWER_THEN * self.max_health > self.health)

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        self._model.delete()

    def save(self):
        self._model.saved_at_turn = TimePrototype.get_current_turn_number()
        self._model.saved_at = datetime.datetime.now()

        if self.bag.updated:
            self.bag.serialize()

        if self.equipment.updated:
            self._model.raw_power = self.power
            self.equipment.serialize()

        if self.abilities.updated:
            self.abilities.serialize()

        if self.places_history.updated:
            self.places_history.serialize()

        if self.messages.updated:
            self._model.messages = s11n.to_json(self.messages.serialize())
            self.messages.updated = False

        if self.diary.updated:
            self.diary.serialize()

        if self.actions.updated:
            self.actions.on_save()
            self._model.actions = s11n.to_json(self.actions.serialize())
            self.actions.updated = False

        if self.quests.updated:
            self._model.quest_created_time = self.quests.min_quest_created_time
            self.quests.serialize()

        if self.pvp.updated:
            self.pvp.serialize()

        if self.preferences.updated:
            self._model.preferences = s11n.to_json(self.preferences.serialize())
            self.preferences.updated = False

        database.raw_save(self._model)

    def reset_level(self):
        self._model.level = 1
        self.abilities.reset()

    def randomize_equip(self):
        for slot in relations.EQUIPMENT_SLOT.records:
            self.equipment.unequip(slot)

            artifacts_list = artifacts_storage.artifacts_for_type([slot.artifact_type])
            if not artifacts_list:
                continue

            artifact = artifacts_storage.generate_artifact_from_list(artifacts_list, self.level)

            self.equipment.equip(slot, artifact)


    def randomized_level_up(self, increment_level=False):
        if increment_level:
            self.increment_level()

        if self.abilities.can_choose_new_ability:
            choices = self.abilities.get_for_choose()

            if not choices:
                return

            new_ability = random.choice(choices)
            if self.abilities.has(new_ability.get_id()):
                self.abilities.increment_level(new_ability.get_id())
            else:
                self.abilities.add(new_ability.get_id())

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

    def ui_info(self, actual_guaranteed):
        from the_tale.game.map.generator.drawer import get_hero_sprite

        return {'id': self.id,
                'actual_on_turn': TimePrototype.get_current_turn_number() if actual_guaranteed else self.saved_at_turn,
                'ui_caching_started_at': time.mktime(self.ui_caching_started_at.timetuple()),
                'messages': self.messages.ui_info(),
                'diary': self.diary.ui_info(with_date=True),
                'position': self.position.ui_info(),
                'bag': self.bag.ui_info(),
                'equipment': self.equipment.ui_info(),
                'might': { 'value': self.might,
                           'crit_chance': self.might_crit_chance,
                           'pvp_effectiveness_bonus': self.might_pvp_effectiveness_bonus },
                'permissions': { 'can_participate_in_pvp': self.can_participate_in_pvp,
                                 'can_repair_building': self.can_repair_building },
                'energy': { 'max': self.energy_maximum,
                            'value': self.energy,
                            'bonus': self.energy_bonus},
                'action': self.actions.current_action.ui_info(),
                # 'pvp' will be filled in modify_ui_info_with_turn
                'pvp__actual': self.pvp.ui_info(),
                'pvp__last_turn': self.pvp.turn_ui_info(),
                'base': { 'name': self.name,
                          'level': self.level,
                          'destiny_points': self.abilities.destiny_points,
                          'health': int(self.health),
                          'max_health': int(self.max_health),
                          'experience': int(self.experience),
                          'experience_to_level': int(f.exp_on_lvl(self.level)),
                          'gender': self.gender.value,
                          'race': self.race.value,
                          'money': self.money,
                          'alive': self.is_alive},
                'secondary': { 'power': math.floor(self.power),
                               'move_speed': float(self.move_speed),
                               'initiative': self.initiative,
                               'max_bag_size': self.max_bag_size,
                               'loot_items_count': self.bag.occupation},
                'habits': { 'honor': {'verbose': self.habit_honor.verbose_value,
                                      'raw': self.habit_honor.raw_value},
                            'peacefulness': {'verbose': self.habit_peacefulness.verbose_value,
                                             'raw': self.habit_peacefulness.raw_value}},
                'quests': self.quests.ui_info(self),
                'sprite': get_hero_sprite(self).value
                }

    @classmethod
    def modify_ui_info_with_turn(self, data, for_last_turn):

        if for_last_turn:
            data['pvp'] = data['pvp__last_turn']
        else:
            data['pvp'] = data['pvp__actual']

        del data['pvp__last_turn']
        del data['pvp__actual']


    def ui_info_for_cache(self, actual_guaranteed):
        return self.ui_info(actual_guaranteed=actual_guaranteed)


    @classmethod
    def cached_ui_info_key_for_hero(cls, account_id):
        return heroes_settings.UI_CACHING_KEY % account_id

    @property
    def cached_ui_info_key(self):
        return self.cached_ui_info_key_for_hero(self.account_id)

    @classmethod
    def cached_ui_info_for_hero(cls, account_id):
        from the_tale.game.workers.environment import workers_environment as game_workers_environment

        data = cache.get(cls.cached_ui_info_key_for_hero(account_id))

        if data is None or cls.is_ui_continue_caching_required(data['ui_caching_started_at']):
            hero = cls.get_by_account_id(account_id)
            data = hero.ui_info_for_cache(actual_guaranteed=False)
            game_workers_environment.supervisor.cmd_start_hero_caching(hero.account_id, hero.id)

        return data

    @classmethod
    def create(cls, account, bundle): # pylint: disable=R0914
        from the_tale.game.relations import GENDER, RACE
        from the_tale.game.actions.prototypes import ActionIdlenessPrototype
        from the_tale.game.logic_storage import LogicStorage

        start_place = places_storage.random_place()

        race = random.choice(RACE.records)

        gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

        current_turn_number = TimePrototype.get_current_turn_number()

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
                                   saved_at_turn=current_turn_number,
                                   active_state_end_at=account.active_end_at,
                                   premium_state_end_at=account.premium_end_at,
                                   account=account._model,
                                   gender=gender,
                                   race=race,
                                   is_fast=account.is_fast,
                                   is_bot=account.is_bot,
                                   abilities=s11n.to_json(AbilitiesPrototype.create().serialize()),
                                   messages=s11n.to_json(messages.serialize()),
                                   diary=s11n.to_json(diary.serialize()),
                                   name=name,
                                   next_spending=relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT,
                                   health=f.hp_on_lvl(1),
                                   energy=c.ANGEL_ENERGY_MAX,
                                   pos_place = start_place._model)

        hero = cls(model=hero)

        HeroPreferencesPrototype.create(hero,
                                        energy_regeneration_type=hero.preferences.energy_regeneration_type,
                                        risk_level=relations.RISK_LEVEL.NORMAL)

        storage = LogicStorage() # tmp storage for creating Idleness action

        storage.add_hero(hero)

        ActionIdlenessPrototype.create(hero=hero, _bundle_id=bundle.id, _storage=storage)

        return hero

    def update_with_account_data(self, is_fast, premium_end_at, active_end_at, ban_end_at, might):
        self.is_fast = is_fast
        self.active_state_end_at = active_end_at
        self.premium_state_end_at = premium_end_at
        self.ban_state_end_at = ban_end_at
        self.might = might

    def cmd_update_with_account_data(self, account):
        from the_tale.game.workers.environment import workers_environment as game_workers_environment

        game_workers_environment.supervisor.cmd_update_hero_with_account_data(account.id,
                                                                              self.id,
                                                                              is_fast=account.is_fast,
                                                                              premium_end_at=account.premium_end_at,
                                                                              active_end_at=account.active_end_at,
                                                                              ban_end_at=account.ban_game_end_at,
                                                                              might=account.might)


    ###########################################
    # Game operations
    ###########################################

    def kill(self):
        self.health = 1
        self.is_alive = False

    def resurrect(self):
        self.health = self.max_health
        self.is_alive = True


    def get_achievement_account_id(self):
        return self.account_id

    def get_achievement_type_value(self, achievement_type):

        if achievement_type.is_TIME:
            return f.turns_to_game_time(self.last_rare_operation_at_turn - self.created_at_turn)[0]
        elif achievement_type.is_MONEY:
            return self.statistics.money_earned
        elif achievement_type.is_MOBS:
            return self.statistics.pve_kills
        elif achievement_type.is_ARTIFACTS:
            return self.statistics.artifacts_had
        elif achievement_type.is_QUESTS:
            return self.statistics.quests_done
        elif achievement_type.is_DEATHS:
            return self.statistics.pve_deaths

        raise exceptions.UnkwnownAchievementTypeError(achievement_type=achievement_type)

    def process_rare_operations(self):
        from the_tale.accounts.achievements.storage import achievements_storage
        from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

        current_turn = TimePrototype.get_current_turn_number()

        passed_interval = current_turn - self.last_rare_operation_at_turn

        if passed_interval < heroes_settings.RARE_OPERATIONS_INTERVAL:
            return

        self.quests.sync_interfered_persons()

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.TIME, object=self):
            self.last_rare_operation_at_turn = current_turn


        habits_multiplier = float(passed_interval) / (24 * c.TURNS_IN_HOUR)

        self.update_habits(relations.HABIT_CHANGE_SOURCE.PERIODIC_LEFT, multuplier=habits_multiplier)
        self.update_habits(relations.HABIT_CHANGE_SOURCE.PERIODIC_RIGHT, multuplier=habits_multiplier)




class HeroPositionPrototype(object):

    def __init__(self, hero_model):
        self.hero_model = hero_model

    @property
    def place_id(self): return self.hero_model.pos_place_id

    @property
    def place(self): return places_storage.get(self.hero_model.pos_place_id)

    @property
    def previous_place(self): return places_storage.get(self.hero_model.pos_previous_place_id)

    def visit_current_place(self):
        self.hero_model.pos_previous_place = self.hero_model.pos_place

    def _reset_position(self):
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

        percents = self.percents

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

    def get_nearest_place(self):
        x, y = self.cell_coordinates
        best_distance = 999999999999999
        best_place = None
        for place in places_storage.all():
            distance = math.hypot(place.x-x, place.y-y)
            if distance < best_distance:
                best_distance = distance
                best_place = place

        return best_place

    def get_nearest_dominant_place(self):
        place = self.get_dominant_place()
        if place is None:
            place = self.get_nearest_place()
        return place

    def is_battle_start_needed(self):
        dominant_place = self.get_dominant_place()

        if dominant_place is not None:
            battles_per_turn = 1.0 - dominant_place.safety
        else:
            battles_per_turn = c.BATTLES_PER_TURN

        return random.uniform(0, 1) <= battles_per_turn


    def modify_move_speed(self, speed):
        dominant_place = self.get_dominant_place()

        if dominant_place is not None:
            return speed * dominant_place.transport
        else:
            return speed

    def get_minumum_distance_to(self, destination):
        from the_tale.game.map.roads.storage import waymarks_storage

        if self.place:
            return waymarks_storage.look_for_road(self.place, destination).length

        if self.is_walking:
            x = self.coordinates_from[0] + (self.coordinates_to[0] - self.coordinates_from[0]) * self.percents
            y = self.coordinates_from[1] + (self.coordinates_to[1] - self.coordinates_from[1]) * self.percents
            nearest_place = self.get_nearest_place()
            return math.hypot(x-nearest_place.x, y-nearest_place.y) + waymarks_storage.look_for_road(nearest_place, destination).length

        # if on road
        place_from = self.road.point_1
        place_to = self.road.point_2

        if self.invert_direction:
            place_from, place_to = place_to, place_from

        delta_from = self.road.length * self.percents
        delta_to = self.road.length * (1-self.percents)

        return min(waymarks_storage.look_for_road(place_from, destination).length + delta_from,
                   waymarks_storage.look_for_road(place_to, destination).length + delta_to)



    def get_position_on_map(self):

        if self.place:
            return (self.place.x, self.place.y, 0, 0)

        if self.road:
            percents = self.percents
            path = self.road.path

            x = self.road.point_1.x
            y = self.road.point_1.y

            dx = self.road.point_1.x - self.road.point_2.x
            dy = self.road.point_1.y - self.road.point_2.y

            if self.invert_direction:
                percents = 1 - percents
                dx = -dx
                dy = -dy

            length = percents * len(path)
            index = 0
            character = None

            for c in path:
                character = c

                index += 1

                if index > length:
                    break

                if c == 'l': x -= 1
                elif c == 'r': x += 1
                elif c == 'u': y -= 1
                elif c == 'd': y += 1

            else:
                index += 1

            delta = length - (index-1)

            if character == 'l': x -= delta
            elif character == 'r': x += delta
            elif character == 'u': y -= delta
            elif character == 'd': y += delta

            return (x, y, dx, dy)

        if self.is_walking:

            to_x = self.coordinates_to[0]
            to_y = self.coordinates_to[1]
            from_x = self.coordinates_from[0]
            from_y = self.coordinates_from[1]

            x = from_x + (to_x - from_x) * self.percents
            y = from_y + (to_y - from_y) * self.percents

            return (x, y, from_x - to_x, from_y - to_y)



    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        x, y, dx, dy = self.get_position_on_map()
        return { 'x': x,
                 'y': y,
                 'dx': dx,
                 'dy': dy}

    def __eq__(self, other):
        return ( self.place_id == other.place_id and
                 self.road_id == other.road_id and
                 self.percents == other.percents and
                 self.invert_direction == other.invert_direction and
                 self.coordinates_from == other.coordinates_from and
                 self.coordinates_to == other.coordinates_to)


class HeroPreferencesPrototype(BasePrototype):
    _model_class = HeroPreferences
    _readonly = ('id',
                 'hero_id',
                 'energy_regeneration_type',
                 'mob_id',
                 'place_id',
                 'friend_id',
                 'enemy_id',
                 'equipment_slot',
                 'risk_level',
                 'favorite_item')
    _bidirectional = ()
    _get_by = ('id', 'hero_id')

    def __init__(self, **kwargs):
        super(HeroPreferencesPrototype, self).__init__(**kwargs)

    @classmethod
    def create(cls, hero, energy_regeneration_type, risk_level):
        return cls(model=cls._model_class.objects.create(hero=hero._model,
                                                         energy_regeneration_type=energy_regeneration_type,
                                                         risk_level=risk_level))

    @classmethod
    def update(cls, hero_id, field, value):
        cls._model_class.objects.filter(hero_id=hero_id).update(**{field: value})
