# coding: utf-8

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from game.actions.models import MetaAction, MetaActionMember, UNINITIALIZED_STATE

from game.actions import battle, contexts

from game.prototypes import TimePrototype

from game.pvp.prototypes import Battle1x1Prototype, BATTLE_1X1_STATE, BATTLE_RESULT


def get_meta_actions_types():
    actions = {}
    for key, cls in globals().items():
        if isinstance(cls, type) and issubclass(cls, MetaActionPrototype) and cls != MetaActionPrototype:
            actions[cls.TYPE] = cls
    return actions


def get_meta_action_by_model(model):
    if model is None:
        return None

    return META_ACTION_TYPES[model.type](model=model)


class MetaActionPrototype(object):

    TYPE = None
    TEXTGEN_TYPE = None

    class STATE:
        UNINITIALIZED = UNINITIALIZED_STATE
        PROCESSED = 'processed'

    def __init__(self, model, members=None):
        self.model = model

        if members is None:
            members = [MetaActionMemberPrototype(member_model) for member_model in MetaActionMember.objects.filter(action=model)]

        self.members = dict( (member.id, member) for member in members)
        self.members_by_roles = dict( (member.role, member) for member in members)
        self.storage = None
        self.last_processed_turn = -1
        self.updated = False

    @property
    def id(self): return self.model.id

    @property
    def created_at(self): return self.model.created_at

    @property
    def type(self): return self.model.type

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def description_text_name(self):
        return '%s_description' % self.TEXTGEN_TYPE

    def set_storage(self, storage): self.storage = storage

    def get_percents(self): return self.model.percents
    def set_percents(self, value): self.model.percents = value
    percents = property(get_percents, set_percents)

    def get_state(self): return self.model.state
    def set_state(self, value): self.model.state = value
    state = property(get_state, set_state)


    def process(self):
        turn_number = TimePrototype.get_current_turn_number()
        if self.last_processed_turn < turn_number:
            self.last_processed_turn = turn_number
            self.updated = True
            self._process()


    def _process(self):
        pass


    def remove(self):
        self.model.delete()

    def save(self):
        if hasattr(self, '_data'):
            self.model.data = s11n.to_json(self._data)
        self.model.save()
        self.updated = False


class MetaActionMemberPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def role(self): return self.model.role

    @property
    def context_str(self): return self.model.context

    @classmethod
    def create(cls, meta_action_model, hero_model, role):

        model = MetaActionMember.objects.create(action=meta_action_model,
                                                hero=hero_model,
                                                role=role)

        return cls(model)


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
            self._hero_1_context = contexts.BattleContext.deserialize(s11n.from_json(self.members_by_roles[self.ROLES.HERO_1].context_str))
        return self._hero_1_context

    @property
    def hero_2(self): return self.storage.heroes[self.members_by_roles[self.ROLES.HERO_2].hero_id]

    def get_hero_2_old_health(self): return self.data.get('hero_2_old_health')
    def set_hero_2_old_health(self, value): self.data['hero_2_old_health'] = value
    hero_2_old_health = property(get_hero_2_old_health, set_hero_2_old_health)

    @property
    def hero_2_context(self):
        if not hasattr(self, '_hero_2_context'):
            self._hero_2_context = contexts.BattleContext.deserialize(s11n.from_json(self.members_by_roles[self.ROLES.HERO_2].context_str))
        return self._hero_2_context

    def add_message(self, *argv, **kwargs):
        self.hero_1.add_message(*argv, **kwargs)
        self.hero_2.add_message(*argv, **kwargs)

    @classmethod
    @nested_commit_on_success
    def create(cls, storage, hero_1, hero_2):

        hero_1_old_health = hero_1.health
        hero_2_old_health = hero_2.health

        hero_1.health = hero_1.max_health
        hero_2.health = hero_2.max_health

        model = MetaAction.objects.create(type=cls.TYPE,
                                          percents=0,
                                          data=s11n.to_json({'hero_1_old_health': hero_1_old_health,
                                                             'hero_2_old_health': hero_2_old_health}),
                                          state=cls.STATE.BATTLE_RUNNING )

        member_1 = MetaActionMemberPrototype.create(meta_action_model=model, hero_model=hero_1.model, role=cls.ROLES.HERO_1)
        member_2 = MetaActionMemberPrototype.create(meta_action_model=model, hero_model=hero_2.model, role=cls.ROLES.HERO_2)

        meta_action = cls(model, members=[member_1, member_2])
        meta_action.set_storage(storage)

        meta_action.add_message('meta_action_arena_pvp_1x1_start', duelist_1=hero_1, duelist_2=hero_2)

        return meta_action


    def _check_hero_health(self, hero, enemy):
        if hero.health <= 0:
            # hero.statistics.change_pve_deaths(1)
            self.add_message('meta_action_arena_pvp_1x1_kill', important=True, victim=hero, killer=enemy)
            self.state = self.STATE.BATTLE_ENDING
            self.percents = 1.0


    def _process(self):

        # check processed state before battle turn, to give delay to players to see battle result

        if self.state == self.STATE.BATTLE_ENDING:
            battle_1 = Battle1x1Prototype.get_active_by_account_id(self.hero_1.account_id)
            battle_1.set_state(BATTLE_1X1_STATE.PROCESSED)

            battle_2 = Battle1x1Prototype.get_active_by_account_id(self.hero_2.account_id)
            battle_2.set_state(BATTLE_1X1_STATE.PROCESSED)

            if battle_1.calculate_rating and battle_2.calculate_rating:
                self.hero_1.statistics.change_pvp_battles_1x1_number(1)
                self.hero_2.statistics.change_pvp_battles_1x1_number(1)

            if self.hero_1.health <= 0:
                if self.hero_2.health <= 0:
                    battle_1.set_result(BATTLE_RESULT.DRAW)
                    battle_2.set_result(BATTLE_RESULT.DRAW)

                    if battle_1.calculate_rating and battle_2.calculate_rating:
                        self.hero_1.statistics.change_pvp_battles_1x1_draws(1)
                        self.hero_2.statistics.change_pvp_battles_1x1_draws(1)
                else:
                    battle_1.set_result(BATTLE_RESULT.DEFEAT)
                    battle_2.set_result(BATTLE_RESULT.VICTORY)

                    if battle_1.calculate_rating and battle_2.calculate_rating:
                        self.hero_2.statistics.change_pvp_battles_1x1_victories(1)
            else:
                battle_1.set_result(BATTLE_RESULT.VICTORY)
                battle_2.set_result(BATTLE_RESULT.DEFEAT)

                if battle_1.calculate_rating and battle_2.calculate_rating:
                    self.hero_1.statistics.change_pvp_battles_1x1_victories(1)

            battle_1.save()
            battle_2.save()

            self.hero_1.health = self.hero_1_old_health
            self.hero_2.health = self.hero_2_old_health

            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.BATTLE_RUNNING:

            if self.hero_1.health > 0 and self.hero_2.health > 0:
                battle.make_turn(battle.Actor(self.hero_1, self.hero_1_context),
                                 battle.Actor(self.hero_2, self.hero_2_context ),
                                 self)

                self.percents = 1.0 - min(self.hero_1.health_percents, self.hero_2.health_percents)

            self._check_hero_health(self.hero_1, self.hero_2)
            self._check_hero_health(self.hero_2, self.hero_1)


META_ACTION_TYPES = get_meta_actions_types()
