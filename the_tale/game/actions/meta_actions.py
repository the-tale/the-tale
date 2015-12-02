# coding: utf-8
import random

from dext.common.utils import discovering

from the_tale.common.utils.logic import random_value_by_priority

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.pvp.abilities import ABILITIES as PVP_ABILITIES

from the_tale.game import relations as game_relations

from the_tale.game.pvp.prototypes import Battle1x1Prototype, Battle1x1ResultPrototype
from the_tale.game.pvp.relations import BATTLE_1X1_RESULT

from . import battle
from . import contexts
from . import relations


class MetaAction(object):
    __slots__ = ('percents', 'state', 'last_processed_turn', 'storage', 'updated', 'uid')

    TYPE = None
    TEXTGEN_TYPE = None

    class STATE:
        UNINITIALIZED = relations.UNINITIALIZED_STATE
        PROCESSED = 'processed'

    def __init__(self, last_processed_turn=-1, percents=0, state=STATE.UNINITIALIZED, uid=NotImplemented):
        self.storage = None
        self.last_processed_turn = last_processed_turn
        self.updated = False

        self.percents = percents
        self.state = state
        self.uid = uid

    def serialize(self):
        return {'type': self.TYPE.value,
                'last_processed_turn': self.last_processed_turn,
                'state': self.state,
                'percents': self.percents,
                'uid': self.uid}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.last_processed_turn = data['last_processed_turn']
        obj.state = data['state']
        obj.percents = data['percents']
        obj.uid = data['uid']

        return obj

    @property
    def description_text_name(self):
        return '%s_description' % self.TEXTGEN_TYPE

    def set_storage(self, storage): self.storage = storage

    def process(self):
        turn_number = TimePrototype.get_current_turn_number()
        if self.last_processed_turn < turn_number:
            self.last_processed_turn = turn_number
            self.updated = True
            self._process()


    def _process(self):
        pass


class ArenaPvP1x1(MetaAction):
    __slots__ = ('hero_1_context', 'hero_2_context', 'hero_1_old_health', 'hero_2_old_health', 'bot_pvp_properties', 'hero_1_id', 'hero_2_id')

    TYPE = relations.ACTION_TYPE.ARENA_PVP_1X1
    TEXTGEN_TYPE = 'meta_action_arena_pvp_1x1'

    class STATE(MetaAction.STATE):
        BATTLE_RUNNING = 'battle_running'
        BATTLE_ENDING = 'battle_ending'

    def __init__(self, hero_1_old_health=None, hero_2_old_health=None, hero_1_context=None, hero_2_context=None, bot_pvp_properties=None, hero_1_id=None, hero_2_id=None, **kwargs):
        super(ArenaPvP1x1, self).__init__(**kwargs)
        self.hero_1_context = hero_1_context
        self.hero_2_context = hero_2_context
        self.hero_1_old_health = hero_1_old_health
        self.hero_2_old_health = hero_2_old_health
        self.bot_pvp_properties = bot_pvp_properties
        self.hero_1_id = hero_1_id
        self.hero_2_id = hero_2_id

        self.uid = '%s#%s#%s' % (self.TYPE.value, min(hero_1_id, hero_2_id), max(hero_1_id, hero_2_id))

    def serialize(self):
        data = super(ArenaPvP1x1, self).serialize()
        data.update({'hero_1_old_health': self.hero_1_old_health,
                     'hero_2_old_health': self.hero_2_old_health,
                     'hero_1_context': self.hero_1_context.serialize(),
                     'hero_2_context': self.hero_2_context.serialize(),
                     'bot_pvp_properties': self.bot_pvp_properties,
                     'hero_1_id': self.hero_1_id,
                     'hero_2_id': self.hero_2_id})
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(ArenaPvP1x1, cls).deserialize(data)

        obj.hero_1_id = data['hero_1_id']
        obj.hero_2_id = data['hero_2_id']
        obj.hero_1_old_health = data['hero_1_old_health']
        obj.hero_2_old_health = data['hero_2_old_health']
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
        cls.reset_hero_info(hero_1)

        hero_2.health = hero_2.max_health
        cls.reset_hero_info(hero_2)

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
                          bot_pvp_properties=cls.get_bot_pvp_properties())

        meta_action.set_storage(storage)

        meta_action.add_message('meta_action_arena_pvp_1x1_start', duelist_1=hero_1, duelist_2=hero_2)

        return meta_action

    @classmethod
    def get_bot_pvp_properties(cls):
        bot_priorities = {ability.TYPE: random.uniform(0.1, 1.0) for ability in PVP_ABILITIES.values()}
        bot_priorities_sum = sum(bot_priorities.values())
        bot_priorities = {ability_type: ability_priority/bot_priorities_sum
                          for ability_type, ability_priority in bot_priorities.items()}
        return {'priorities': bot_priorities, 'ability_chance': random.uniform(0.1, 0.33)}


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
    def reset_hero_info(cls, hero):
        hero.pvp.set_advantage(0)
        hero.pvp.set_effectiveness(c.PVP_EFFECTIVENESS_INITIAL)
        hero.pvp.set_energy(0)
        hero.pvp.set_energy_speed(1)

        hero.pvp.store_turn_data()

    @classmethod
    def prepair_bot(cls, hero, enemy):
        if not hero.is_bot:
            return

        hero.preferences.set_archetype(random.choice(game_relations.ARCHETYPE.records))

        hero.reset_level()
        for i in xrange(enemy.level-1):
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

    def update_hero_pvp_info(self, hero):
        hero.pvp.set_energy(hero.pvp.energy + hero.pvp.energy_speed)
        hero.pvp.set_effectiveness(hero.pvp.effectiveness - hero.pvp.effectiveness * c.PVP_EFFECTIVENESS_EXTINCTION_FRACTION)

    def process_battle_ending(self):
        battle_1 = Battle1x1Prototype.get_by_account_id(self.hero_1.account_id)
        battle_2 = Battle1x1Prototype.get_by_account_id(self.hero_2.account_id)

        participant_1 = AccountPrototype.get_by_id(self.hero_1.account_id)
        participant_2 = AccountPrototype.get_by_id(self.hero_2.account_id)

        if self.hero_1.health <= 0:
            if self.hero_2.health <= 0:
                Battle1x1ResultPrototype.create(participant_1=participant_1, participant_2=participant_2, result =BATTLE_1X1_RESULT.DRAW)

                if battle_1.calculate_rating and battle_2.calculate_rating:
                    self.hero_1.statistics.change_pvp_battles_1x1_draws(1)
                    self.hero_2.statistics.change_pvp_battles_1x1_draws(1)
            else:
                Battle1x1ResultPrototype.create(participant_1=participant_1, participant_2=participant_2, result =BATTLE_1X1_RESULT.DEFEAT)

                if battle_1.calculate_rating and battle_2.calculate_rating:
                    self.hero_2.statistics.change_pvp_battles_1x1_victories(1)
                    self.hero_1.statistics.change_pvp_battles_1x1_defeats(1)
        else:
            Battle1x1ResultPrototype.create(participant_1=participant_1, participant_2=participant_2, result =BATTLE_1X1_RESULT.VICTORY)

            if battle_1.calculate_rating and battle_2.calculate_rating:
                self.hero_1.statistics.change_pvp_battles_1x1_victories(1)
                self.hero_2.statistics.change_pvp_battles_1x1_defeats(1)

        battle_1.remove()
        battle_2.remove()

        self.hero_1.health = self.hero_1_old_health
        self.hero_2.health = self.hero_2_old_health

        self.reset_hero_info(self.hero_1)
        self.reset_hero_info(self.hero_2)

        self.state = self.STATE.PROCESSED

    def process_bot(self, bot, enemy):
        from the_tale.game.pvp.abilities import Flame

        properties = self.bot_pvp_properties

        if random.uniform(0.0, 1.0) > properties['ability_chance']:
            return

        used_ability_type = random_value_by_priority(properties['priorities'].items())

        if used_ability_type == Flame.TYPE and enemy.pvp.energy_speed == 1:
            return

        PVP_ABILITIES[used_ability_type](hero=bot, enemy=enemy).use()


    def process_battle_running(self):
        # apply all changes made by player
        hero_1_effectivenes = self.hero_1.pvp.effectiveness
        hero_2_effectivenes = self.hero_2.pvp.effectiveness

        if self.hero_1.is_bot:
            self.process_bot(bot=self.hero_1, enemy=self.hero_2)

        if self.hero_2.is_bot:
            self.process_bot(bot=self.hero_2, enemy=self.hero_1)

        # modify advantage
        max_effectivenes = float(max(hero_1_effectivenes, hero_2_effectivenes))
        if max_effectivenes < 0.01:
            effectiveness_fraction = 0
        else:
            effectiveness_fraction = (hero_1_effectivenes - hero_2_effectivenes) / max_effectivenes
        advantage_delta = c.PVP_MAX_ADVANTAGE_STEP * effectiveness_fraction

        self.hero_1.pvp.set_advantage(self.hero_1.pvp.advantage + advantage_delta)
        self.hero_1_context.use_pvp_advantage(self.hero_1.pvp.advantage)

        self.hero_2.pvp.set_advantage(self.hero_2.pvp.advantage - advantage_delta)
        self.hero_2_context.use_pvp_advantage(self.hero_2.pvp.advantage)

        # battle step
        if self.hero_1.health > 0 and self.hero_2.health > 0:
            battle.make_turn(battle.Actor(self.hero_1, self.hero_1_context),
                             battle.Actor(self.hero_2, self.hero_2_context ),
                             self)

            if self.hero_1_context.pvp_advantage_used or self.hero_2_context.pvp_advantage_used:
                self.hero_1.pvp.set_advantage(0)
                self.hero_2.pvp.set_advantage(0)

            self.percents = 1.0 - min(self.hero_1.health_percents, self.hero_2.health_percents)

        # update resources, etc
        self.update_hero_pvp_info(self.hero_1)
        self.update_hero_pvp_info(self.hero_2)

        self.hero_1.pvp.store_turn_data()
        self.hero_2.pvp.store_turn_data()

        # check if anyone has killed
        self._check_hero_health(self.hero_1, self.hero_2)
        self._check_hero_health(self.hero_2, self.hero_1)


    def _process(self):

        # check processed state before battle turn, to give delay to players to see battle result

        if self.state == self.STATE.BATTLE_ENDING:
            self.process_battle_ending()

        if self.state == self.STATE.BATTLE_RUNNING:
            self.process_battle_running()



ACTION_TYPES = { action_class.TYPE:action_class
                 for action_class in discovering.discover_classes(globals().values(), MetaAction) }
