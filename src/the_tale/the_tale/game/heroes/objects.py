
import smart_imports

smart_imports.all()


class Hero(logic_accessors.LogicAccessorsMixin,
           equipment_methods.EquipmentMethodsMixin,
           jobs_methods.JobsMethodsMixin,
           game_names.ManageNameMixin2):

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

                 'force_save_required',
                 'last_help_on_turn',
                 'helps_in_turn',
                 'level',
                 'experience',
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
                 'health',
                 'quests',
                 'abilities',
                 'bag',
                 'equipment',
                 'actual_bills',

                 'upbringing',
                 'death_age',
                 'first_death',

                 'utg_name',

                 'clan_id',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    _bidirectional = ()

    def __init__(self,
                 id,
                 account_id,
                 clan_id,
                 level,
                 experience,
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
                 health,
                 quests,
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
                 actual_bills,
                 utg_name,
                 upbringing,
                 death_age,
                 first_death):

        self.id = id
        self.account_id = account_id
        self.clan_id = clan_id

        self.force_save_required = False

        self.last_help_on_turn = 0
        self.helps_in_turn = 0

        self.health = health

        self.level = level
        self.experience = experience

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

        self.quests = quests
        self.quests.initialize(hero=self)

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

        self.upbringing = upbringing
        self.death_age = death_age
        self.first_death = first_death

        self.utg_name = utg_name

    def clan_membership(self):
        if self.clan_id is None:
            return relations.CLAN_MEMBERSHIP.NOT_IN_CLAN

        return relations.CLAN_MEMBERSHIP.IN_CLAN

    ##########################
    # experience
    ##########################

    def increment_level(self, send_message=False):
        self.level += 1

        self.add_message('hero_common_journal_level_up', hero=self, level=self.level)

        self.force_save_required = True

        if send_message:  # TODO: move out logic
            personal_messages_logic.send_message(sender_id=accounts_logic.get_system_user_id(),
                                                 recipients_ids=[self.account_id],
                                                 body='Поздравляем, Ваш герой получил {} уровень!'.format(self.level),
                                                 asynchronous=True)

    def add_experience(self, value, without_modifications=False):
        real_experience = int(value) if without_modifications else int(value * self.experience_modifier)
        self.experience += real_experience

        while self.experience_to_next_level <= self.experience:
            self.experience -= self.experience_to_next_level
            self.increment_level(send_message=True)

        return real_experience

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

        logic.register_spending(self, value)

        self.statistics.change_money(source, abs(value))
        self.money += value

    def switch_spending(self):
        spending_candidates = self.spending_priorities()

        if self.companion is None or self.companion_heal_disabled():
            spending_candidates[relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION] = 0

        self.next_spending = utils_logic.random_value_by_priority(list(spending_candidates.items()))
        self.quests.mark_updated()

    ##########################
    # quests
    ##########################

    def get_quests_priorities(self):
        # always check hero position to prevent «bad» quests generation
        quests = [quest for quest in quests_relations.QUESTS.records if quest.quest_type.is_NORMAL]

        if self.preferences.mob is not None:
            quests.append(quests_relations.QUESTS.HUNT)
        if self.preferences.place is not None and (self.position.place is None or self.preferences.place.id != self.position.place.id):
            quests.append(quests_relations.QUESTS.HOMETOWN)
        if self.preferences.friend is not None and (self.position.place is None or self.preferences.friend.place.id != self.position.place.id):
            quests.append(quests_relations.QUESTS.HELP_FRIEND)
        if self.preferences.enemy is not None and (self.position.place is None or self.preferences.enemy.place.id != self.position.place.id):
            quests.append(quests_relations.QUESTS.INTERFERE_ENEMY)

        if any(place._modifier.is_HOLY_CITY for place in places_storage.places.all()):
            if self.position.place is None or not self.position.place._modifier.is_HOLY_CITY:
                quests.append(quests_relations.QUESTS.PILGRIMAGE)

        return [(quest, self.modify_quest_priority(quest)) for quest in quests]

    ##########################
    # habits
    ##########################

    def update_habits(self, change_source, multuplier=1.0):

        if change_source.quest_default is False:
            multuplier *= self.habit_quest_active_multiplier

        if change_source.correlation_requirements is None:
            self.habit_honor.change(change_source.honor * multuplier)
            self.habit_peacefulness.change(change_source.peacefulness * multuplier)

        elif change_source.correlation_requirements:
            if self.habit_honor.raw_value * change_source.honor > 0:
                self.habit_honor.change(change_source.honor * multuplier)
            if self.habit_peacefulness.raw_value * change_source.peacefulness > 0:
                self.habit_peacefulness.change(change_source.peacefulness * multuplier)

        else:
            if self.habit_honor.raw_value * change_source.honor < 0:
                self.habit_honor.change(change_source.honor * multuplier)
            if self.habit_peacefulness.raw_value * change_source.peacefulness < 0:
                self.habit_peacefulness.change(change_source.peacefulness * multuplier)

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
            size = conf.settings.DIARY_LOG_LENGTH_PREMIUM if self.is_premium else conf.settings.DIARY_LOG_LENGTH

            tt_services.diary.cmd_push_message(self.id, message, size=size)

    def add_message(self, type_, diary=False, journal=True, turn_delta=0, **kwargs):
        if not diary and not self.is_active and not self.is_premium:
            # do not process journal messages for inactive heroes (and clear them if needed)
            self.journal.clear()
            return

        lexicon_key, externals, restrictions = linguistics_logic.prepair_get_text(type_, kwargs)

        message_constructor = messages.MessageSurrogate.create

        if lexicon_key is None:
            message_constructor = messages.MessageSurrogate.create_fake

        message = message_constructor(key=lexicon_key if lexicon_key else type_,
                                      externals=externals,
                                      turn_delta=turn_delta,
                                      restrictions=restrictions,
                                      position=self.position.get_description() if diary else '')

        self.push_message(message, diary=diary, journal=journal)

    ##########################
    # callbacks
    ##########################

    def on_help(self):
        current_turn = game_turn.number()

        if self.last_help_on_turn != current_turn:
            self.last_help_on_turn = current_turn
            self.helps_in_turn = 0

        self.helps_in_turn += 1

    ##########################
    # service
    ##########################

    def update_with_account_data(self, is_fast, premium_end_at, active_end_at, ban_end_at, might, actual_bills, clan_id):
        self.is_fast = is_fast
        self.active_state_end_at = active_end_at
        self.premium_state_end_at = premium_end_at
        self.ban_state_end_at = ban_end_at
        self.might = might
        self.actual_bills = actual_bills
        self.clan_id = clan_id

    def get_achievement_account_id(self):
        return self.account_id

    def get_achievement_type_value(self, achievement_type):

        if achievement_type.is_TIME:
            return game_turn.game_datetime(self.last_rare_operation_at_turn - self.created_at_turn).year
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
            if self.statistics.pvp_battles_1x1_number >= conf.settings.MIN_PVP_BATTLES:
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
        current_turn = game_turn.number()

        passed_interval = current_turn - self.last_rare_operation_at_turn

        if passed_interval < conf.settings.RARE_OPERATIONS_INTERVAL:
            return

        if self.companion is None and random.random() < float(passed_interval) / c.TURNS_IN_HOUR / c.COMPANIONS_GIVE_COMPANION_AFTER:
            companions_choices = [companion for companion in companions_storage.companions.enabled_companions()
                                  if any(ability.effect.TYPE.is_LEAVE_HERO for ability in companion.abilities.start)]
            if companions_choices:
                self.set_companion(companions_logic.create_companion(random.choice(companions_choices)))

        self.quests.sync_interfered_persons()

        with achievements_storage.achievements.verify(type=achievements_relations.ACHIEVEMENT_TYPE.TIME, object=self):
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
                self.journal == other.journal)

    ##########################
    # ui info
    ##########################

    def ui_info(self, actual_guaranteed, old_info=None):
        from the_tale.forum.jinjaglobals import scify_race

        path = self.actions.find_path()

        new_info = {'id': self.id,
                    'patch_turn': None if old_info is None else old_info['actual_on_turn'],
                    'actual_on_turn': game_turn.number() if actual_guaranteed else self.saved_at_turn,
                    'ui_caching_started_at': time.mktime(self.ui_caching_started_at.timetuple()),
                    'diary': None,  # diary version will be setupped by game:info view
                    'messages': self.journal.ui_info(),
                    'position': self.position.ui_info(),
                    'bag': self.bag.ui_info(self),
                    'equipment': self.equipment.ui_info(self),
                    'might': {'value': self.might,
                              'crit_chance': self.might_crit_chance,
                              'pvp_effectiveness_bonus': self.might_pvp_effectiveness_bonus,
                              'politics_power': self.politics_power_might},
                    'permissions': {'can_participate_in_pvp': self.can_participate_in_pvp,
                                    'can_repair_building': False},  # deprecated, remove in future releases
                    'action': self.actions.current_action.ui_info(),
                    'path': path.ui_info() if path else None,
                    'companion': self.companion.ui_info() if self.companion else None,
                    'base': {'name': self.name,
                             'level': self.level,
                             'destiny_points': self.abilities.destiny_points,
                             'health': int(self.health),
                             'max_health': int(self.max_health),
                             'experience': int(self.experience),
                             'experience_to_level': int(self.experience_to_next_level),
                             'gender': self.gender.value,
                             'race': self.race.value,
                             'scify_race': scify_race(self.id).ui_info(),
                             'money': self.money,
                             'alive': self.is_alive},
                    'secondary': {'power': self.power.ui_info(),
                                  'move_speed': float(self.move_speed),
                                  'initiative': self.initiative,
                                  'max_bag_size': self.max_bag_size,
                                  'loot_items_count': self.bag.occupation},
                    'habits': {game_relations.HABIT_TYPE.HONOR.verbose_value: {'verbose': self.habit_honor.verbose_value,
                                                                               'raw': self.habit_honor.raw_value},
                               game_relations.HABIT_TYPE.PEACEFULNESS.verbose_value: {'verbose': self.habit_peacefulness.verbose_value,
                                                                                      'raw': self.habit_peacefulness.raw_value}},
                    'quests': self.quests.ui_info(self),
                    'sprite': map_generator.drawer.get_hero_sprite(self).value}

        changed_fields = ['changed_fields', 'actual_on_turn', 'patch_turn']

        if old_info:
            for key, value in new_info.items():
                if old_info[key] != value:
                    changed_fields.append(key)

        new_info['changed_fields'] = changed_fields

        return new_info

    @classmethod
    def modify_ui_info_with_turn(cls, data, for_last_turn):

        action_data = data['action']['data']

        if action_data is None or not action_data.get('is_pvp'):
            return

        if for_last_turn:
            action_data['pvp'] = action_data['pvp__last_turn']
        else:
            action_data['pvp'] = action_data['pvp__actual']

        del action_data['pvp__last_turn']
        del action_data['pvp__actual']

    @classmethod
    def cached_ui_info_key_for_hero(cls, account_id):
        return conf.settings.UI_CACHING_KEY % account_id

    @property
    def cached_ui_info_key(self):
        return self.cached_ui_info_key_for_hero(self.account_id)

    @classmethod
    def reset_ui_cache(cls, account_id):
        utils_cache.delete(cls.cached_ui_info_key_for_hero(account_id))

    @classmethod
    def cached_ui_info_for_hero(cls, account_id, recache_if_required, patch_turns, for_last_turn):
        data = utils_cache.get(cls.cached_ui_info_key_for_hero(account_id))

        if data is None:
            hero = logic.load_hero(account_id=account_id)
            data = hero.ui_info(actual_guaranteed=False)

        cls.modify_ui_info_with_turn(data, for_last_turn=for_last_turn)

        if recache_if_required and cls.is_ui_continue_caching_required(data['ui_caching_started_at']) and game_prototypes.GameState.is_working():
            amqp_environment.environment.workers.supervisor.cmd_start_hero_caching(account_id)

        if patch_turns is not None and data['patch_turn'] in patch_turns:
            patch_fields = set(data['changed_fields'])
            for field in list(data.keys()):

                # action always required, since it is used in game.logic
                if field == 'action':
                    continue

                if field not in patch_fields:
                    del data[field]
        else:
            data['patch_turn'] = None

        del data['changed_fields']

        return data

    def new_cards_combined(self, number):
        self.statistics.change_cards_combined(number)

    def meta_object(self):
        return meta_relations.Hero.create_from_object(self)
