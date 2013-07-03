# coding: utf-8

from dext.utils import cache

from game.heroes.prototypes import HeroPrototype
from game.heroes.conf import heroes_settings

from game import exceptions
from game.conf import game_settings


class LogicStorage(object):

    def __init__(self=None):
        self.heroes = {}
        self.accounts_to_heroes = {}
        self.meta_actions = {}
        self.meta_actions_to_actions = {}
        self.skipped_heroes = set()

    def load_account_data(self, account):
        hero = HeroPrototype.get_by_account_id(account.id)
        hero.update_with_account_data(is_fast=account.is_fast,
                                      premium_end_at=account.premium_end_at,
                                      active_end_at=account.active_end_at,
                                      ban_end_at=account.ban_game_end_at)
        self.add_hero(hero)

    def release_account_data(self, account, save_required=True):
        hero = self.accounts_to_heroes[account.id]

        if save_required:
            self.save_hero_data(hero.id, update_cache=True)

        if hero.id in self.skipped_heroes:
            self.skipped_heroes.remove(hero.id)

        del self.heroes[hero.id]
        del self.accounts_to_heroes[account.id]

    def save_account_data(self, account_id, update_cache):
        return self.save_hero_data(self.accounts_to_heroes[account_id].id, update_cache=update_cache)

    def save_hero_data(self, hero_id, update_cache):
        hero = self.heroes[hero_id]
        hero.save()

        if update_cache:
            cache.set(hero.cached_ui_info_key, hero.ui_info_for_cache(), heroes_settings.UI_CACHING_TIMEOUT)


    def add_hero(self, hero):

        if hero.id in self.heroes:
            raise exceptions.HeroAlreadyRegisteredError(hero_id=hero.id)

        self.heroes[hero.id] = hero
        self.accounts_to_heroes[hero.account_id] = hero

        for action in hero.actions.actions_list:
            self.add_action(action)

    def add_action(self, action):
        action.set_storage(self)

        if action.meta_action_id is not None:

            if action.meta_action_id not in self.meta_actions_to_actions:
                self.meta_actions_to_actions[action.meta_action_id] = set()
            self.meta_actions_to_actions[action.meta_action_id].add(self.get_action_uid(action))

            if action.meta_action_id not in self.meta_actions:
                from game.actions.models import MetaAction
                from game.actions.meta_actions import get_meta_action_by_model
                self.add_meta_action(get_meta_action_by_model(MetaAction.objects.get(id=action.meta_action_id)))


    def add_meta_action(self, meta_action):
        if meta_action.id in self.meta_actions:
            raise exceptions.GameException('Meta action with id "%d" has already registerd in storage' % meta_action.id)
        meta_action.set_storage(self)
        self.meta_actions[meta_action.id] = meta_action

    def remove_action(self, action):
        action.set_storage(None)
        last_action = action.hero.actions.current_action
        if last_action is not action:
            raise exceptions.RemoveActionFromMiddleError(action=action, last_action=last_action, actions_list=action.hero.actions.actions_list)

        if action.meta_action_id is not None:
            self.meta_actions_to_actions[action.meta_action_id].remove(self.get_action_uid(action))
            if not self.meta_actions_to_actions[action.meta_action_id]:
                del self.meta_actions_to_actions[action.meta_action_id]
                self.meta_actions[action.meta_action_id].remove()
                del self.meta_actions[action.meta_action_id]

    @classmethod
    def get_action_uid(cls, action):
        number = action.hero.actions.number
        return (action.hero.id, number - 1 if action is action.hero.actions.current_action else number)

    def on_highlevel_data_updated(self):
        for hero in self.heroes.values():
            hero.on_highlevel_data_updated()


    def process_turn(self):

        for hero in self.heroes.values():

            if hero.id in self.skipped_heroes:
                continue

            leader_action = hero.actions.current_action
            bundle_id = leader_action.bundle_id

            try:
                leader_action.process_turn()
            except Exception:
                self._save_on_exception(excluded_bundle_id=bundle_id)
                raise

            if leader_action.removed and leader_action.bundle_id != hero.actions.current_action.bundle_id:
                self.skipped_heroes.add(hero.id)

    def _save_on_exception(self, excluded_bundle_id):
        for hero_id, hero in self.heroes.iteritems():
            if hero.actions.current_action.bundle_id == excluded_bundle_id:
                continue
            self.save_hero_data(hero_id, update_cache=False)

    def save_all(self):
        for hero_id, hero in self.heroes.iteritems():
            self.save_hero_data(hero_id, update_cache=False)

    def _get_bundles_to_save(self):
        bundles = set(hero.actions.current_action.bundle_id for hero in self.heroes.itervalues() if hero.is_ui_caching_required)

        unsaved_heroes = sorted(self.heroes.itervalues(), key=lambda h: h.saved_at)

        saved_uncached_heroes_number = int(game_settings.SAVED_UNCACHED_HEROES_FRACTION * len(self.heroes) + 1)

        bundles.update(hero.actions.current_action.bundle_id for hero in unsaved_heroes[:saved_uncached_heroes_number])

        return bundles

    def save_changed_data(self):
        cached_ui_info = {}

        bundles = self._get_bundles_to_save()

        for hero_id, hero in self.heroes.iteritems():

            if hero.actions.current_action.bundle_id not in bundles:
                continue

            self.save_hero_data(hero_id, update_cache=False)

            if hero.is_ui_caching_required:
                cached_ui_info[hero.cached_ui_info_key] = hero.ui_info_for_cache()

        cache.set_many(cached_ui_info, heroes_settings.UI_CACHING_TIMEOUT)

    def _destroy_account_data(self, account):

        hero = self.accounts_to_heroes[account.id]

        for action in reversed(hero.actions.actions_list):
            action.remove()

        self.release_account_data(account, save_required=False)

        hero.remove()

    def _test_save(self):
        for hero_id in self.heroes:
            self.save_hero_data(hero_id, update_cache=False)

        test_storage = LogicStorage()
        for hero_id in self.heroes:
            test_storage.add_hero(HeroPrototype.get_by_id(hero_id))

        return self == test_storage

    def __eq__(self, other):
        return (self.heroes == other.heroes and
                self.accounts_to_heroes == other.accounts_to_heroes)
