# coding: utf-8
import random

from django.db import transaction

from dext.utils import s11n

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.actions.models import MetaAction, MetaActionMember, UNINITIALIZED_STATE
from the_tale.game.actions import battle, contexts

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c

from the_tale.game.pvp.prototypes import Battle1x1Prototype, Battle1x1ResultPrototype
from the_tale.game.pvp.relations import BATTLE_1X1_RESULT


def get_meta_actions_types():
    actions = {}
    for cls in globals().values():
        if isinstance(cls, type) and issubclass(cls, MetaActionPrototype) and cls != MetaActionPrototype:
            actions[cls.TYPE] = cls
    return actions


def get_meta_action_by_model(model):
    if model is None:
        return None

    return META_ACTION_TYPES[model.type](model=model)


class MetaActionPrototype(BasePrototype):
    _model_class = MetaAction
    _readonly = ('id', 'created_at', 'type')
    _bidirectional = ('percents', 'state')
    _get_by = ('id',)

    TYPE = None
    TEXTGEN_TYPE = None

    class STATE:
        UNINITIALIZED = UNINITIALIZED_STATE
        PROCESSED = 'processed'

    def __init__(self, model, members=None):
        super(MetaActionPrototype, self).__init__(model=model)

        if members is None:
            members = [MetaActionMemberPrototype(member_model) for member_model in MetaActionMember.objects.filter(action=model)]

        self.members = dict( (member.id, member) for member in members)
        self.members_by_roles = dict( (member.role, member) for member in members)
        self.storage = None
        self.last_processed_turn = -1
        self.updated = False

    @lazy_property
    def data(self): return s11n.from_json(self._model.data)

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


    def remove(self):
        from the_tale.game.bundles import BundlePrototype
        MetaActionMemberPrototype._model_class.objects.filter(action_id=self.id).delete()
        self._model.delete()
        BundlePrototype.delete_by_id(self._model.bundle_id)

    def save(self):
        if hasattr(self, '_data'):
            self._model.data = s11n.to_json(self._data)
        self._model.save()
        self.updated = False


class MetaActionMemberPrototype(BasePrototype):
    _model_class = MetaActionMember
    _readonly = ('id', 'hero_id', 'role', 'context')
    _bidirectional = ('percents', 'state')
    _get_by = ('id',)

    @classmethod
    def create(cls, meta_action_model, hero_model, role):

        model = MetaActionMember.objects.create(action=meta_action_model,
                                                hero=hero_model,
                                                role=role)

        return cls(model=model)


class MetaActionArenaPvP1x1Prototype(MetaActionPrototype):

    TYPE = 'ARENA_PVP_1X1'
    TEXTGEN_TYPE = 'meta_action_arena_pvp_1x1'

    class STATE(MetaActionPrototype.STATE):
        BATTLE_RUNNING = 'battle_running'
        BATTLE_ENDING = 'battle_ending'

    class ROLES(object):
        HERO_1 = 'hero_1'
        HERO_2 = 'hero_2'

    @property
    def hero_1(self): return self.storage.heroes[self.members_by_roles[self.ROLES.HERO_1].hero_id]

    def get_hero_1_old_health(self): return self.data.get('hero_1_old_health')
    def set_hero_1_old_health(self, value): self.data['hero_1_old_health'] = value
    hero_1_old_health = property(get_hero_1_old_health, set_hero_1_old_health)

    @property
    def hero_1_context(self):
        if not hasattr(self, '_hero_1_context'):
            self._hero_1_context = contexts.BattleContext.deserialize(s11n.from_json(self.members_by_roles[self.ROLES.HERO_1].context))
            self._hero_1_context.use_pvp_advantage_stike_damage(self.hero_1.basic_damage * c.DAMAGE_PVP_FULL_ADVANTAGE_STRIKE_MODIFIER)
        return self._hero_1_context

    @property
    def hero_2(self): return self.storage.heroes[self.members_by_roles[self.ROLES.HERO_2].hero_id]

    def get_hero_2_old_health(self): return self.data.get('hero_2_old_health')
    def set_hero_2_old_health(self, value): self.data['hero_2_old_health'] = value
    hero_2_old_health = property(get_hero_2_old_health, set_hero_2_old_health)

    @property
    def hero_2_context(self):
        if not hasattr(self, '_hero_2_context'):
            self._hero_2_context = contexts.BattleContext.deserialize(s11n.from_json(self.members_by_roles[self.ROLES.HERO_2].context))
            self._hero_2_context.use_pvp_advantage_stike_damage(self.hero_2.basic_damage * c.DAMAGE_PVP_FULL_ADVANTAGE_STRIKE_MODIFIER)
        return self._hero_2_context

    def get_bot_pvp_properties(self):
        from the_tale.game.pvp.abilities import ABILITIES

        if 'bot_pvp_properties' in self.data:
            return self.data['bot_pvp_properties']

        priorities = {ability.TYPE: random.uniform(0.1, 1.0) for ability in ABILITIES.values()}
        priorities_sum = sum(priorities.values())
        priorities = {ability_type: ability_priority/priorities_sum
                      for ability_type, ability_priority in priorities.items()}

        self.data['bot_pvp_properties'] = {'priorities': priorities,
                                           'ability_chance': random.uniform(0.1, 0.33)}
        return self.data['bot_pvp_properties']

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

        hero.reset_level()
        for i in xrange(enemy.level-1):
            hero.randomized_level_up(increment_level=True)
        hero.randomize_equip()


    @classmethod
    @transaction.atomic
    def create(cls, storage, hero_1, hero_2, bundle):

        cls.prepair_bot(hero_1, hero_2)
        cls.prepair_bot(hero_2, hero_1)

        hero_1_old_health = hero_1.health
        hero_2_old_health = hero_2.health

        hero_1.health = hero_1.max_health
        cls.reset_hero_info(hero_1)

        hero_2.health = hero_2.max_health
        cls.reset_hero_info(hero_2)

        model = MetaAction.objects.create(type=cls.TYPE,
                                          percents=0,
                                          data=s11n.to_json({'hero_1_old_health': hero_1_old_health,
                                                             'hero_2_old_health': hero_2_old_health}),
                                          bundle=bundle._model,
                                          state=cls.STATE.BATTLE_RUNNING )

        member_1 = MetaActionMemberPrototype.create(meta_action_model=model, hero_model=hero_1._model, role=cls.ROLES.HERO_1)
        member_2 = MetaActionMemberPrototype.create(meta_action_model=model, hero_model=hero_2._model, role=cls.ROLES.HERO_2)

        meta_action = cls(model, members=[member_1, member_2])
        meta_action.set_storage(storage)

        meta_action.add_message('meta_action_arena_pvp_1x1_start', duelist_1=hero_1, duelist_2=hero_2)

        return meta_action


    def _check_hero_health(self, hero, enemy):
        if hero.health <= 0:
            # hero.statistics.change_pve_deaths(1)
            self.add_message('meta_action_arena_pvp_1x1_diary_kill', diary=True, victim=hero, killer=enemy)
            self.state = self.STATE.BATTLE_ENDING
            self.percents = 1.0

    def update_hero_pvp_info(self, hero):
        hero.pvp.set_energy(hero.pvp.energy + hero.pvp.energy_speed)
        hero.pvp.set_effectiveness(hero.pvp.effectiveness - hero.pvp.effectiveness * c.PVP_EFFECTIVENESS_EXTINCTION_FRACTION)

    def process_battle_ending(self):
        battle_1 = Battle1x1Prototype.get_by_account_id(self.hero_1.account_id)
        battle_2 = Battle1x1Prototype.get_by_account_id(self.hero_2.account_id)

        if battle_1.calculate_rating and battle_2.calculate_rating:
            self.hero_1.statistics.change_pvp_battles_1x1_number(1)
            self.hero_2.statistics.change_pvp_battles_1x1_number(1)

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
        else:
            Battle1x1ResultPrototype.create(participant_1=participant_1, participant_2=participant_2, result =BATTLE_1X1_RESULT.VICTORY)

            if battle_1.calculate_rating and battle_2.calculate_rating:
                self.hero_1.statistics.change_pvp_battles_1x1_victories(1)

        battle_1.remove()
        battle_2.remove()

        self.hero_1.health = self.hero_1_old_health
        self.hero_2.health = self.hero_2_old_health

        self.reset_hero_info(self.hero_1)
        self.reset_hero_info(self.hero_2)

        self.state = self.STATE.PROCESSED

    def process_bot(self, bot, enemy):
        from the_tale.game.pvp.abilities import ABILITIES

        properties = self.get_bot_pvp_properties()

        if random.uniform(0.0, 1.0) > properties['ability_chance']:
            return

        used_ability_type = random_value_by_priority(properties['priorities'].items())

        ABILITIES[used_ability_type](hero=bot, enemy=enemy).use()


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



META_ACTION_TYPES = get_meta_actions_types()
