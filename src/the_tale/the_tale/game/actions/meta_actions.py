
import smart_imports

smart_imports.all()


class MetaAction(object):
    __slots__ = ('percents', 'state', 'last_processed_turn', 'storage')

    TYPE = None
    TEXTGEN_TYPE = NotImplemented

    class STATE:
        UNINITIALIZED = relations.UNINITIALIZED_STATE
        PROCESSED = 'processed'

    def __init__(self, last_processed_turn=-1, percents=0, state=None):
        if state is None:
            state = self.STATE.UNINITIALIZED

        self.storage = None
        self.last_processed_turn = last_processed_turn

        self.percents = percents
        self.state = state

    def serialize(self):
        return {'type': self.TYPE.value,
                'last_processed_turn': self.last_processed_turn,
                'state': self.state,
                'percents': self.percents}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.last_processed_turn = data['last_processed_turn']
        obj.state = data['state']
        obj.percents = data['percents']

        return obj

    def is_valid(self):
        return False

    def cancel(self):
        pass

    @property
    def description_text_name(self):
        return '%s_description' % self.TEXTGEN_TYPE

    def set_storage(self, storage):
        self.storage = storage

    def process(self):
        turn_number = game_turn.number()

        if self.last_processed_turn < turn_number:
            self.last_processed_turn = turn_number
            self._process()

    def _process(self):
        pass

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)


class ArenaPvP1x1(MetaAction):
    __slots__ = ('hero_1_context', 'hero_2_context', 'hero_1_old_health', 'hero_2_old_health', 'bot_pvp_properties', 'hero_1_id', 'hero_2_id', 'hero_1_pvp', 'hero_2_pvp')

    TYPE = relations.ACTION_TYPE.ARENA_PVP_1X1
    TEXTGEN_TYPE = 'meta_action_arena_pvp_1x1'

    class STATE(MetaAction.STATE):
        BATTLE_RUNNING = 'battle_running'
        BATTLE_ENDING = 'battle_ending'

    def __init__(self,
                 hero_1_old_health=None,
                 hero_2_old_health=None,
                 hero_1_context=None,
                 hero_2_context=None,
                 bot_pvp_properties=None,
                 hero_1_id=None,
                 hero_2_id=None,
                 hero_1_pvp=None,
                 hero_2_pvp=None,
                 **kwargs):
        super(ArenaPvP1x1, self).__init__(**kwargs)
        self.hero_1_context = hero_1_context
        self.hero_2_context = hero_2_context
        self.hero_1_old_health = hero_1_old_health
        self.hero_2_old_health = hero_2_old_health
        self.bot_pvp_properties = bot_pvp_properties
        self.hero_1_id = hero_1_id
        self.hero_2_id = hero_2_id
        self.hero_1_pvp = hero_1_pvp
        self.hero_2_pvp = hero_2_pvp

    def help_choices(self):
        return ()

    @property
    def uid(self):
        return '%s#%s#%s' % (self.TYPE.value, min(self.hero_1_id, self.hero_2_id), max(self.hero_1_id, self.hero_2_id))

    def serialize(self):
        data = super(ArenaPvP1x1, self).serialize()
        data.update({'hero_1_old_health': self.hero_1_old_health,
                     'hero_2_old_health': self.hero_2_old_health,
                     'hero_1_context': self.hero_1_context.serialize(),
                     'hero_2_context': self.hero_2_context.serialize(),
                     'bot_pvp_properties': self.bot_pvp_properties,
                     'hero_1_id': self.hero_1_id,
                     'hero_2_id': self.hero_2_id,
                     'hero_1_pvp': self.hero_1_pvp.serialize(),
                     'hero_2_pvp': self.hero_2_pvp.serialize()})
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(ArenaPvP1x1, cls).deserialize(data)

        obj.hero_1_id = data['hero_1_id']
        obj.hero_2_id = data['hero_2_id']
        obj.hero_1_old_health = data['hero_1_old_health']
        obj.hero_2_old_health = data['hero_2_old_health']
        obj.hero_1_pvp = pvp.PvPData.deserialize(data['hero_1_pvp']) if 'hero_1_pvp' in data else pvp.PvPData()
        obj.hero_2_pvp = pvp.PvPData.deserialize(data['hero_2_pvp']) if 'hero_2_pvp' in data else pvp.PvPData()
        obj.hero_1_context = contexts.BattleContext.deserialize(data['hero_1_context'])
        obj.hero_2_context = contexts.BattleContext.deserialize(data['hero_2_context'])
        obj.bot_pvp_properties = data['bot_pvp_properties']

        return obj

    @classmethod
    def create(cls, storage, hero_1, hero_2):

        cls.prepair_bot(hero_1, hero_2)
        cls.prepair_bot(hero_2, hero_1)

        hero_1_old_health = hero_1.health
        hero_2_old_health = hero_2.health

        hero_1.health = hero_1.max_health
        hero_2.health = hero_2.max_health

        hero_1_context = contexts.BattleContext()
        hero_1_context.use_pvp_advantage_stike_damage(hero_1.basic_damage * c.DAMAGE_PVP_FULL_ADVANTAGE_STRIKE_MODIFIER)

        hero_2_context = contexts.BattleContext()
        hero_2_context.use_pvp_advantage_stike_damage(hero_2.basic_damage * c.DAMAGE_PVP_FULL_ADVANTAGE_STRIKE_MODIFIER)

        meta_action = cls(hero_1_id=hero_1.id,
                          hero_2_id=hero_2.id,
                          hero_1_old_health=hero_1_old_health,
                          hero_2_old_health=hero_2_old_health,
                          hero_1_context=hero_1_context,
                          hero_2_context=hero_2_context,
                          state=cls.STATE.BATTLE_RUNNING,
                          hero_1_pvp=pvp.PvPData(),
                          hero_2_pvp=pvp.PvPData(),
                          bot_pvp_properties=cls.get_bot_pvp_properties())

        meta_action.set_storage(storage)

        meta_action.add_message('meta_action_arena_pvp_1x1_start', duelist_1=hero_1, duelist_2=hero_2)

        return meta_action

    @classmethod
    def get_bot_pvp_properties(cls):
        bot_priorities = {ability.TYPE: random.uniform(0.1, 1.0) for ability in pvp_abilities.ABILITIES.values()}
        bot_priorities_sum = sum(bot_priorities.values())
        bot_priorities = {ability_type: ability_priority / bot_priorities_sum
                          for ability_type, ability_priority in bot_priorities.items()}
        return {'priorities': bot_priorities, 'ability_chance': random.uniform(0.1, 0.33)}

    def ui_info(self, hero):
        if hero.id == self.hero_1_id:
            info = self.hero_1_pvp
            enemy_id = self.hero_2_id
        else:
            info = self.hero_2_pvp
            enemy_id = self.hero_1_id

        return {'is_pvp': True,
                'enemy_id': enemy_id,
                'pvp__actual': info.ui_info(),
                'pvp__last_turn': info.turn_ui_info()}

    def is_valid(self):
        return self.hero_1 is not None and self.hero_2 is not None

    @property
    def hero_1(self):
        return self.storage.heroes.get(self.hero_1_id)

    @property
    def hero_2(self):
        return self.storage.heroes.get(self.hero_2_id)

    def add_message(self, *argv, **kwargs):
        self.hero_1.add_message(*argv, **kwargs)
        self.hero_2.add_message(*argv, **kwargs)

    @classmethod
    def prepair_bot(cls, hero, enemy):
        if not hero.is_bot:
            return

        hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ARCHETYPE, random.choice(game_relations.ARCHETYPE.records))

        hero.reset_level()
        for i in range(enemy.level - 1):
            hero.randomized_level_up(increment_level=True)
        hero.randomize_equip()

        if not companions_storage.companions.is_empty():
            companion_record = random.choice(companions_storage.companions.all())
            hero.set_companion(companions_logic.create_companion(companion_record))

    def _check_hero_health(self, hero, enemy):
        if hero.health <= 0:
            self.add_message('meta_action_arena_pvp_1x1_kill', victim=hero, killer=enemy)
            self.state = self.STATE.BATTLE_ENDING
            self.percents = 1.0

    def update_hero_pvp_info(self, pvp):
        pvp.set_energy(pvp.energy + pvp.energy_speed)
        pvp.set_effectiveness(pvp.effectiveness - pvp.effectiveness * c.PVP_EFFECTIVENESS_EXTINCTION_FRACTION)

    def process_battle_ending(self):
        participant_1 = accounts_prototypes.AccountPrototype.get_by_id(self.hero_1.account_id)
        participant_2 = accounts_prototypes.AccountPrototype.get_by_id(self.hero_2.account_id)

        calculate_rating = pvp_logic.calculate_rating_required(self.hero_1, self.hero_2)

        if self.hero_1.health <= 0:
            if self.hero_2.health <= 0:
                pvp_prototypes.Battle1x1ResultPrototype.create(participant_1=participant_1,
                                                               participant_2=participant_2,
                                                               result=pvp_relations.BATTLE_1X1_RESULT.DRAW)

                if calculate_rating:
                    self.hero_1.statistics.change_pvp_battles_1x1_draws(1)
                    self.hero_2.statistics.change_pvp_battles_1x1_draws(1)
            else:
                pvp_prototypes.Battle1x1ResultPrototype.create(participant_1=participant_1,
                                                               participant_2=participant_2,
                                                               result=pvp_relations.BATTLE_1X1_RESULT.DEFEAT)

                if calculate_rating:
                    self.hero_2.statistics.change_pvp_battles_1x1_victories(1)
                    self.hero_1.statistics.change_pvp_battles_1x1_defeats(1)
        else:
            pvp_prototypes.Battle1x1ResultPrototype.create(participant_1=participant_1,
                                                           participant_2=participant_2,
                                                           result=pvp_relations.BATTLE_1X1_RESULT.VICTORY)

            if calculate_rating:
                self.hero_1.statistics.change_pvp_battles_1x1_victories(1)
                self.hero_2.statistics.change_pvp_battles_1x1_defeats(1)

        self.finish_battle()

        self.hero_1.health = self.hero_1_old_health
        self.hero_2.health = self.hero_2_old_health

        self.state = self.STATE.PROCESSED

    def finish_battle(self):
        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.hero_1_id,
                                                                                               self.hero_2_id))

        matchmaker_battles_ids = {battle.id for battle in battles}

        for matchmaker_battle_id in matchmaker_battles_ids:
            pvp_tt_services.matchmaker.cmd_finish_battle(matchmaker_battle_id)

    def cancel(self):
        self.finish_battle()
        self.percents = 1.0
        self.state = self.STATE.PROCESSED

    def process_bot(self, bot, enemy, enemy_pvp):
        properties = self.bot_pvp_properties

        if random.uniform(0.0, 1.0) > properties['ability_chance']:
            return

        used_ability_type = utils_logic.random_value_by_priority(properties['priorities'].items())

        if used_ability_type == pvp_abilities.Flame.TYPE and enemy_pvp.energy_speed == 1:
            return

        pvp_abilities.ABILITIES[used_ability_type](hero=bot, enemy=enemy).use()

    def process_battle_running(self):
        # apply all changes made by player
        hero_1_effectivenes = self.hero_1_pvp.effectiveness
        hero_2_effectivenes = self.hero_2_pvp.effectiveness

        if self.hero_1.is_bot:
            self.process_bot(bot=self.hero_1, enemy=self.hero_2, enemy_pvp=self.hero_2_pvp)

        if self.hero_2.is_bot:
            self.process_bot(bot=self.hero_2, enemy=self.hero_1, enemy_pvp=self.hero_1_pvp)

        # modify advantage
        max_effectivenes = float(max(hero_1_effectivenes, hero_2_effectivenes))
        if max_effectivenes < 0.01:
            effectiveness_fraction = 0
        else:
            effectiveness_fraction = (hero_1_effectivenes - hero_2_effectivenes) / max_effectivenes
        advantage_delta = c.PVP_MAX_ADVANTAGE_STEP * effectiveness_fraction

        self.hero_1_pvp.set_advantage(self.hero_1_pvp.advantage + advantage_delta)
        self.hero_1_context.use_pvp_advantage(self.hero_1_pvp.advantage)

        self.hero_2_pvp.set_advantage(self.hero_2_pvp.advantage - advantage_delta)
        self.hero_2_context.use_pvp_advantage(self.hero_2_pvp.advantage)

        # battle step
        if self.hero_1.health > 0 and self.hero_2.health > 0:
            battle.make_turn(battle.Actor(self.hero_1, self.hero_1_context),
                             battle.Actor(self.hero_2, self.hero_2_context),
                             self)

            if self.hero_1_context.pvp_advantage_used or self.hero_2_context.pvp_advantage_used:
                self.hero_1_pvp.set_advantage(0)
                self.hero_2_pvp.set_advantage(0)

            self.percents = 1.0 - min(self.hero_1.health_percents, self.hero_2.health_percents)

        # update resources, etc
        self.update_hero_pvp_info(self.hero_1_pvp)
        self.update_hero_pvp_info(self.hero_2_pvp)

        self.hero_1_pvp.store_turn_data()
        self.hero_2_pvp.store_turn_data()

        # check if anyone has killed
        self._check_hero_health(self.hero_1, self.hero_2)
        self._check_hero_health(self.hero_2, self.hero_1)

    def _process(self):

        # check processed state before battle turn, to give delay to players to see battle result

        if self.state == self.STATE.BATTLE_ENDING:
            self.process_battle_ending()

        if self.state == self.STATE.BATTLE_RUNNING:
            self.process_battle_running()

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                super().__eq__(other) and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))


ACTION_TYPES = {action_class.TYPE: action_class
                for action_class in utils_discovering.discover_classes(globals().values(), MetaAction)}
