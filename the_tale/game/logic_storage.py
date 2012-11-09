# coding: utf-8

from game.actions.models import Action

from game.heroes.prototypes import HeroPrototype

from game.exceptions import GameException

class LogicStorage(object):

    def __init__(self=None):
        self.heroes = {}
        self.actions = {}
        self.heroes_to_actions = {}
        self.meta_actions = {}
        self.meta_actions_to_actions = {}
        self.save_requered = set()

    def load_account_data(self, account):

        hero = HeroPrototype.get_by_account_id(account.id)

        # sync hero is_fast state
        hero.is_fast = account.is_fast

        # if hero: # hero can be None if we at process of creating account
        self.add_hero(hero)

    def release_account_data(self, account):
        hero = HeroPrototype.get_by_account_id(account.id)
        self.save_hero_data(hero.id)

        for action_id in Action.objects.filter(hero_id=hero.id).values_list('id', flat=True):
            del self.actions[action_id]

        del self.heroes[hero.id]
        del self.heroes_to_actions[hero.id]


    def save_hero_data(self, hero_id):
        hero = self.heroes[hero_id]
        hero.save()

        for action in self.heroes_to_actions[hero_id]:
            if action.updated:
                action.save()


    def add_hero(self, hero):

        from game.actions.models import Action
        from game.actions.prototypes import ACTION_TYPES


        if hero.id in self.heroes:
            raise GameException('Hero with id "%d" has already registerd in storage, probably on initialization step' % hero.id)

        self.heroes[hero.id] = hero
        self.heroes_to_actions[hero.id] = []

        for action_model in list(Action.objects.filter(hero_id=hero.id).order_by('order')):
            self.add_action(ACTION_TYPES[action_model.type](model=action_model))

    def add_action(self, action):
        action.set_storage(self)
        self.actions[action.id] = action
        self.heroes_to_actions[action.hero_id].append(action)

        if action.meta_action_id is not None:

            if action.meta_action_id not in self.meta_actions_to_actions:
                self.meta_actions_to_actions[action.meta_action_id] = set()
            self.meta_actions_to_actions[action.meta_action_id].add(action.id)

            if action.meta_action_id not in self.meta_actions:
                from game.actions.models import MetaAction
                from game.actions.meta_actions import get_meta_action_by_model
                self.add_meta_action(get_meta_action_by_model(MetaAction.objects.get(id=action.meta_action_id)))


    def add_meta_action(self, meta_action):
        if meta_action.id in self.meta_actions:
            raise GameException('Meta action with id "%d" has already registerd in storage' % meta_action.id)
        meta_action.set_storage(self)
        self.meta_actions[meta_action.id] = meta_action

    def remove_action(self, action):
        del self.actions[action.id]
        action.set_storage(None)
        last_action = self.heroes_to_actions[action.hero_id][-1]
        if last_action.id != action.id:
            raise GameException('try to remove action (%d - %r) from the middle of actions list, last action id: (%d - %r). Actions list: %r' %
                                (action.id, action, last_action.id, last_action, self.heroes_to_actions[action.hero_id]))
        self.heroes_to_actions[action.hero_id].pop()

        if action.meta_action_id is not None:
            self.meta_actions_to_actions[action.meta_action_id].remove(action.id)
            if not self.meta_actions_to_actions[action.meta_action_id]:
                del self.meta_actions_to_actions[action.meta_action_id]
                self.meta_actions[action.meta_action_id].remove()

    def current_hero_action(self, hero_id): return self.heroes_to_actions[hero_id][-1]

    def on_highlevel_data_updated(self):
        for hero in self.heroes.values():
            hero.on_highlevel_data_updated()


    def process_turn(self):

        for hero in self.heroes.values():
            hero.process_turn()

            leader_action = self.heroes_to_actions[hero.id][-1]

            leader_action.process_turn()

            self.save_requered.add(hero.id)

    def save_changed_data(self):
        for hero_id in self.save_requered:
            self.save_hero_data(hero_id)

        self.save_requered.clear()


    def _test_save(self):
        for hero_id in self.heroes:
            self.save_hero_data(hero_id)

        test_storage = LogicStorage()
        for hero_id in self.heroes:
            test_storage.add_hero(HeroPrototype.get_by_id(hero_id))

        return self == test_storage

    def _test_get_hero_by_account_id(self, account_id):
        return self.heroes[HeroPrototype.get_by_account_id(account_id).id]

    def __eq__(self, other):
        return (self.heroes == other.heroes and
                self.actions == other.actions and
                self.heroes_to_actions == other.heroes_to_actions)
