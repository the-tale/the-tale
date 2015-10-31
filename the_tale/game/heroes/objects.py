# coding: utf-8
import math
import time
import random

from dext.common.utils import cache

from the_tale import amqp_environment

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts import logic as accounts_logic
from the_tale.accounts.personal_messages import prototypes as message_prototypes

from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game import names
from the_tale.game.map.places.storage import places_storage

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c

from the_tale.game.prototypes import TimePrototype, GameState
from the_tale.game import relations as game_relations

from . import relations
from . import messages
from . import exceptions
from . import conf
from . import logic_accessors
from . import shop_accessors
from . import equipment_methods


# TODO: merge classes instead subclassing
class Hero(logic_accessors.LogicAccessorsMixin,
           shop_accessors.ShopAccessorsMixin,
           equipment_methods.EquipmentMethodsMixin,
           names.ManageNameMixin2):

    __slots__ = ('id',
                 'account_id',

                 'created_at_turn',
                 'saved_at_turn',
                 'saved_at',
                 'is_bot',
                 'is_alive',
                 'is_fast',
                 'gender',
                 'race',
                 'last_energy_regeneration_at_turn',
                 'might',
                 'ui_caching_started_at',
                 'active_state_end_at',
                 'premium_state_end_at',
                 'ban_state_end_at',
                 'last_rare_operation_at_turn',
                 'settings_approved',

                 'force_save_required',
                 'last_help_on_turn',
                 'helps_in_turn',
                 'level',
                 'experience',
                 'energy',
                 'energy_bonus',
                 'money',
                 'next_spending',
                 'habit_honor',
                 'habit_peacefulness',
                 'position',
                 'statistics',
                 'preferences',
                 'actions',
                 'companion',
                 'journal',
                 'diary',
                 'health',
                 'quests',
                 'places_history',
                 'cards',
                 'pvp',
                 'abilities',
                 'bag',
                 'equipment',
                 'actual_bills',

                 'utg_name',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')


    _bidirectional = ()

    def __init__(self,
                 id,
                 account_id,
                 level,
                 experience,
                 energy,
                 energy_bonus,
                 money,
                 next_spending,
                 habit_honor,
                 habit_peacefulness,
                 position,
                 statistics,
                 preferences,
                 actions,
                 companion,
                 journal,
                 diary,
                 health,
                 quests,
                 places_history,
                 cards,
                 pvp,
                 abilities,
                 bag,
                 equipment,
                 created_at_turn,
                 saved_at_turn,
                 saved_at,
                 is_bot,
                 is_alive,
                 is_fast,
                 gender,
                 race,
                 last_energy_regeneration_at_turn,
                 might,
                 ui_caching_started_at,
                 active_state_end_at,
                 premium_state_end_at,
                 ban_state_end_at,
                 last_rare_operation_at_turn,
                 settings_approved,
                 actual_bills,
                 utg_name):

        self.id = id
        self.account_id = account_id

        self.force_save_required = False

        self.last_help_on_turn = 0
        self.helps_in_turn = 0

        self.health = health

        self.level = level
        self.experience = experience

        self.energy = energy
        self.energy_bonus = energy_bonus

        self.money = money
        self.next_spending = next_spending

        self.habit_honor = habit_honor
        self.habit_honor.owner = self

        self.habit_peacefulness = habit_peacefulness
        self.habit_peacefulness.owner = self

        self.position = position

        self.statistics = statistics
        self.statistics.hero = self

        self.preferences = preferences
        self.preferences.hero = self

        self.actions = actions
        self.actions.initialize(hero=self)

        self.companion = companion
        if self.companion:
            self.companion._hero = self

        self.journal = journal
        self.diary = diary

        self.quests = quests
        self.quests.initialize(hero=self)

        self.places_history = places_history

        self.cards = cards
        self.cards._hero = self

        self.pvp = pvp

        self.abilities = abilities
        self.abilities.hero = self

        self.bag = bag

        self.equipment = equipment
        self.equipment.hero = self

        self.actual_bills = actual_bills

        self.created_at_turn = created_at_turn
        self.saved_at_turn = saved_at_turn
        self.saved_at = saved_at
        self.is_bot = is_bot
        self.is_alive = is_alive
        self.is_fast = is_fast
        self.gender = gender
        self.race = race
        self.last_energy_regeneration_at_turn = last_energy_regeneration_at_turn
        self.might = might
        self.ui_caching_started_at = ui_caching_started_at
        self.active_state_end_at = active_state_end_at
        self.premium_state_end_at = premium_state_end_at
        self.ban_state_end_at = ban_state_end_at
        self.last_rare_operation_at_turn = last_rare_operation_at_turn
        self.settings_approved = settings_approved

        self.utg_name = utg_name

    ##########################
    # experience
    ##########################

    def increment_level(self, send_message=False):
        self.level += 1

        self.add_message('hero_common_journal_level_up', hero=self, level=self.level)

        self.force_save_required = True

        if send_message: # TODO: move out logic
            account = accounts_prototypes.AccountPrototype.get_by_id(self.account_id)
            message_prototypes.MessagePrototype.create(accounts_logic.get_system_user(), account, text=u'Поздравляем, Ваш герой получил %d уровень!' % self.level)

    def add_experience(self, value, without_modifications=False):
        real_experience = int(value) if without_modifications else int(value * self.experience_modifier)
        self.experience += real_experience

        while self.experience_to_next_level <= self.experience:
            self.experience -= self.experience_to_next_level
            self.increment_level(send_message=True)

        return real_experience

    def convert_experience_to_energy(self, energy_cost):
        bonus = int(math.ceil(float(self.experience) / energy_cost))
        self.energy_bonus += bonus
        self.experience = 0
        return bonus

    def reset_level(self):
        self.level = 1
        self.abilities.reset()

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


    ##########################
    # health
    ##########################

    def heal(self, delta):
        if delta < 0:
            raise exceptions.HealHeroForNegativeValueError()
        old_health = self.health
        self.health = int(min(self.health + delta, self.max_health))
        return self.health - old_health

    def kill(self):
        self.health = 1
        self.is_alive = False

    def resurrect(self):
        self.health = self.max_health
        self.is_alive = True

    ##########################
    # money
    ##########################

    def change_money(self, source, value):
        value = int(round(value))
        self.statistics.change_money(source, abs(value))
        self.money += value

    def switch_spending(self):
        spending_candidates = self.spending_priorities()

        if self.companion is None or self.companion_heal_disabled():
            spending_candidates[relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION] = 0

        self.next_spending = random_value_by_priority(list(spending_candidates.items()))
        self.quests.mark_updated()


    ##########################
    # quests
    ##########################

    def get_quests_priorities(self):
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

        if any(place.modifier and place.modifier.TYPE.is_HOLY_CITY for place in places_storage.all()):
            if self.position.place is None or self.position.place.modifier is None or not self.position.place.modifier.TYPE.is_HOLY_CITY:
                quests.append(QUESTS.PILGRIMAGE)

        return [(quest, self.modify_quest_priority(quest)) for quest in quests]

    ##########################
    # energy
    ##########################

    @property
    def energy_full(self):
        return self.energy + self.energy_bonus

    def add_energy_bonus(self, energy):
        self.energy_bonus += energy

    def change_energy(self, value):
        old_energy = self.energy_full

        if value < -1:
            value = min(-1, value + self.energy_discount)

        self.energy += value

        if self.energy < 0:
            self.energy_bonus += self.energy
            self.energy = 0

        elif self.energy > self.energy_maximum:
            self.energy = self.energy_maximum

        if self.energy_bonus < 0:
            self.energy_bonus = 0

        return self.energy_full - old_energy


    ##########################
    # habits
    ##########################

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

    def change_habits(self, habit_type, habit_value):

        if habit_type == self.habit_honor.TYPE:
            self.habit_honor.change(habit_value)

        if habit_type == self.habit_peacefulness.TYPE:
            self.habit_peacefulness.change(habit_value)

    ##########################
    # companion
    ##########################

    def set_companion(self, companion):
        self.statistics.change_companions_count(1)

        if self.companion:
            self.add_message('companions_left', diary=True, companion_owner=self, companion=self.companion)

        self.add_message('companions_received', diary=True, companion_owner=self, companion=companion)

        self.remove_companion()

        self.companion = companion

        if self.companion:
            self.companion._hero = self
            self.companion.on_settupped()

    def remove_companion(self):
        self.companion = None
        self.reset_accessors_cache()

        while self.next_spending.is_HEAL_COMPANION:
            self.switch_spending()


    ##########################
    # messages
    ##########################

    def push_message(self, message, diary=False, journal=True):
        if journal:
            self.journal.push_message(message)

            if diary:
                message = message.clone()

        if diary:
            self.diary.push_message(message)

    def add_message(self, type_, diary=False, journal=True, turn_delta=0, **kwargs):
        from the_tale.linguistics import logic

        if not diary and not self.is_active and not self.is_premium:
            # do not process journal messages for inactive heroes (and clear it if needed)
            self.journal.clear()
            return

        lexicon_key, externals, restrictions = logic.prepair_get_text(type_, kwargs)

        message_constructor = messages.MessageSurrogate.create

        if lexicon_key is None:
            message_constructor = messages.MessageSurrogate.create_fake

        message = message_constructor(key=lexicon_key if lexicon_key else type_,
                                      externals=externals,
                                      turn_delta=turn_delta,
                                      restrictions=restrictions,
                                      position=self.position.get_description() if diary else u'')

        self.push_message(message, diary=diary, journal=journal)


    ##########################
    # callbacks
    ##########################

    def on_help(self):
        current_turn = TimePrototype.get_current_turn_number()

        if self.last_help_on_turn != current_turn:
            self.last_help_on_turn = current_turn
            self.helps_in_turn = 0

        self.helps_in_turn += 1

    ##########################
    # service
    ##########################

    def update_with_account_data(self, is_fast, premium_end_at, active_end_at, ban_end_at, might, actual_bills):
        self.is_fast = is_fast
        self.active_state_end_at = active_end_at
        self.premium_state_end_at = premium_end_at
        self.ban_state_end_at = ban_end_at
        self.might = might
        self.actual_bills = actual_bills

    def on_highlevel_data_updated(self):
        if self.preferences.friend is not None and self.preferences.friend.out_game:
            self.preferences.reset_friend()

        if self.preferences.enemy is not None and self.preferences.enemy.out_game:
            self.preferences.reset_enemy()

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
        elif achievement_type.is_PVP_BATTLES_1X1:
            return self.statistics.pvp_battles_1x1_number
        elif achievement_type.is_PVP_VICTORIES_1X1:
            if self.statistics.pvp_battles_1x1_number >= conf.heroes_settings.MIN_PVP_BATTLES:
                return int(float(self.statistics.pvp_battles_1x1_victories) / self.statistics.pvp_battles_1x1_number * 100)
            return 0
        elif achievement_type.is_KEEPER_HELP_COUNT:
            return self.statistics.help_count
        elif achievement_type.is_HABITS_HONOR:
            return self.habit_honor.raw_value
        elif achievement_type.is_HABITS_PEACEFULNESS:
            return self.habit_peacefulness.raw_value
        elif achievement_type.is_KEEPER_CARDS_USED:
            return self.statistics.cards_used
        elif achievement_type.is_KEEPER_CARDS_COMBINED:
            return self.statistics.cards_combined

        raise exceptions.UnkwnownAchievementTypeError(achievement_type=achievement_type)

    def process_rare_operations(self):
        from the_tale.accounts.achievements.storage import achievements_storage
        from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

        from the_tale.game.companions import storage as companions_storage
        from the_tale.game.companions import logic as companions_logic

        current_turn = TimePrototype.get_current_turn_number()

        passed_interval = current_turn - self.last_rare_operation_at_turn

        if passed_interval < conf.heroes_settings.RARE_OPERATIONS_INTERVAL:
            return

        if self.companion is None and random.random() < float(passed_interval) / c.TURNS_IN_HOUR / c.COMPANIONS_GIVE_COMPANION_AFTER:
            companions_choices = [companion for companion in companions_storage.companions.enabled_companions()
                                  if any(ability.effect.TYPE.is_LEAVE_HERO for ability in companion.abilities.start)]
            if companions_choices:
                self.set_companion(companions_logic.create_companion(random.choice(companions_choices)))

        self.quests.sync_interfered_persons()

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.TIME, object=self):
            self.last_rare_operation_at_turn = current_turn


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
                self.journal == other.journal and
                self.diary == other.diary)

    ##########################
    # ui info
    ##########################

    def ui_info(self, actual_guaranteed, old_info=None):
        from the_tale.game.map.generator.drawer import get_hero_sprite

        new_info = {'id': self.id,
                    'patch_turn': None if old_info is None else old_info['actual_on_turn'],
                    'actual_on_turn': TimePrototype.get_current_turn_number() if actual_guaranteed else self.saved_at_turn,
                    'ui_caching_started_at': time.mktime(self.ui_caching_started_at.timetuple()),
                    'messages': self.journal.ui_info(),
                    'diary': self.diary.ui_info(with_info=True),
                    'position': self.position.ui_info(),
                    'bag': self.bag.ui_info(self),
                    'equipment': self.equipment.ui_info(self),
                    'cards': self.cards.ui_info(),
                    'might': { 'value': self.might,
                               'crit_chance': self.might_crit_chance,
                               'pvp_effectiveness_bonus': self.might_pvp_effectiveness_bonus,
                               'politics_power': self.politics_power_might },
                    'permissions': { 'can_participate_in_pvp': self.can_participate_in_pvp,
                                     'can_repair_building': self.can_repair_building },
                    'energy': { 'max': self.energy_maximum,
                                'value': self.energy,
                                'bonus': self.energy_bonus,
                                'discount': self.energy_discount},
                    'action': self.actions.current_action.ui_info(),
                    'companion': self.companion.ui_info() if self.companion else None,
                    # 'pvp' will be filled in modify_ui_info_with_turn
                    'pvp__actual': self.pvp.ui_info(),
                    'pvp__last_turn': self.pvp.turn_ui_info(),
                    'base': { 'name': self.name,
                              'level': self.level,
                              'destiny_points': self.abilities.destiny_points,
                              'health': int(self.health),
                              'max_health': int(self.max_health),
                              'experience': int(self.experience),
                              'experience_to_level': int(self.experience_to_next_level),
                              'gender': self.gender.value,
                              'race': self.race.value,
                              'money': self.money,
                              'alive': self.is_alive},
                    'secondary': { 'power': self.power.ui_info(),
                                   'move_speed': float(self.move_speed),
                                   'initiative': self.initiative,
                                   'max_bag_size': self.max_bag_size,
                                   'loot_items_count': self.bag.occupation},
                    'habits': { game_relations.HABIT_TYPE.HONOR.verbose_value: {'verbose': self.habit_honor.verbose_value,
                                                                                'raw': self.habit_honor.raw_value},
                                game_relations.HABIT_TYPE.PEACEFULNESS.verbose_value: {'verbose': self.habit_peacefulness.verbose_value,
                                                                                       'raw': self.habit_peacefulness.raw_value}},
                    'quests': self.quests.ui_info(self),
                    'sprite': get_hero_sprite(self).value,
                   }

        changed_fields = ['changed_fields', 'actual_on_turn', 'patch_turn']

        if old_info:
            for key, value in new_info.iteritems():
                if old_info[key] != value:
                    changed_fields.append(key)

        new_info['changed_fields'] = changed_fields

        return new_info

    @classmethod
    def modify_ui_info_with_turn(cls, data, for_last_turn):
        if for_last_turn:
            data['pvp'] = data['pvp__last_turn']
        else:
            data['pvp'] = data['pvp__actual']

        if 'pvp__last_turn' in data['changed_fields'] or 'pvp__actual' in data['changed_fields']:
            data['changed_fields'].append('pvp')

        del data['pvp__last_turn']
        del data['pvp__actual']


    @classmethod
    def cached_ui_info_key_for_hero(cls, account_id):
        return conf.heroes_settings.UI_CACHING_KEY % account_id

    @property
    def cached_ui_info_key(self):
        return self.cached_ui_info_key_for_hero(self.account_id)

    @classmethod
    def cached_ui_info_for_hero(cls, account_id, recache_if_required, patch_turns, for_last_turn):
        from . import logic

        data = cache.get(cls.cached_ui_info_key_for_hero(account_id))

        if data is None:
            hero = logic.load_hero(account_id=account_id)
            data = hero.ui_info(actual_guaranteed=False)

        cls.modify_ui_info_with_turn(data, for_last_turn=for_last_turn)

        if recache_if_required and cls.is_ui_continue_caching_required(data['ui_caching_started_at']) and GameState.is_working():
            amqp_environment.environment.workers.supervisor.cmd_start_hero_caching(account_id)

        if patch_turns is not None and data['patch_turn'] in patch_turns:
            patch_fields = set(data['changed_fields'])
            for field in data.keys():
                if field not in patch_fields:
                    del data[field]
        else:
            data['patch_turn'] = None

        del data['changed_fields']

        return data
