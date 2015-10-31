# coding: utf-8
import sys
import time
import datetime
import contextlib

from django.conf import settings as project_settings

from dext.common.utils import cache

from the_tale.game.heroes.conf import heroes_settings

from the_tale.game import exceptions
from the_tale.game import conf
from the_tale.game.prototypes import TimePrototype

from the_tale.game.heroes import logic as heroes_logic


class LogicStorage(object):

    def __init__(self=None):
        self.heroes = {}
        self.accounts_to_heroes = {}
        self.meta_actions = {}
        self.meta_actions_to_actions = {}
        self.skipped_heroes = set()
        self.bundles_to_accounts = {}
        self.ignored_bundles = set()

        self.previous_cache = {}
        self.current_cache = {}
        self.cache_queue = set()

    def load_account_data(self, account):
        hero = heroes_logic.load_hero(account_id=account.id)
        hero.update_with_account_data(is_fast=account.is_fast,
                                      premium_end_at=account.premium_end_at,
                                      active_end_at=account.active_end_at,
                                      ban_end_at=account.ban_game_end_at,
                                      might=account.might,
                                      actual_bills=account.actual_bills)
        self._add_hero(hero)

        return hero

    def release_account_data(self, account_id, save_required=True):
        hero = self.accounts_to_heroes[account_id]

        if save_required:
            self._save_hero_data(hero.id)

        if hero.id in self.skipped_heroes:
            self.skipped_heroes.remove(hero.id)

        del self.heroes[hero.id]
        del self.accounts_to_heroes[account_id]

        bundle_id = hero.actions.current_action.bundle_id

        self.bundles_to_accounts[bundle_id].remove(account_id)
        if not self.bundles_to_accounts[bundle_id]:
            del self.bundles_to_accounts[bundle_id]

    def save_bundle_data(self, bundle_id):
        for account_id in self.bundles_to_accounts[bundle_id]:
            hero = self.accounts_to_heroes[account_id]
            self._save_hero_data(hero.id)
            self.cache_queue.add(hero.id)

        self.process_cache_queue()

    def recache_bundle(self, bundle_id):
        for account_id in self.bundles_to_accounts[bundle_id]:
            self.cache_queue.add(self.accounts_to_heroes[account_id].id)

        self.process_cache_queue()

    def _save_hero_data(self, hero_id):
        heroes_logic.save_hero(self.heroes[hero_id])

    def _add_hero(self, hero):

        if hero.id in self.heroes:
            raise exceptions.HeroAlreadyRegisteredError(hero_id=hero.id)

        self.heroes[hero.id] = hero
        self.accounts_to_heroes[hero.account_id] = hero

        for action in hero.actions.actions_list:
            self.add_action(action)

        bundle_id = hero.actions.current_action.bundle_id

        if bundle_id not in self.bundles_to_accounts:
            self.bundles_to_accounts[bundle_id] = set()
        self.bundles_to_accounts[bundle_id].add(hero.account_id)


    def merge_bundles(self, bundles_from, bundle_into):

        accounts = set()

        for bundle_id in bundles_from:
            accounts |= self.bundles_to_accounts[bundle_id]
            del self.bundles_to_accounts[bundle_id]

        self.bundles_to_accounts[bundle_into] = self.bundles_to_accounts.get(bundle_into, set()) |  accounts

    def unmerge_bundles(self, account_id, old_bundle_id, new_bundle_id):
        self.bundles_to_accounts[old_bundle_id].remove(account_id)

        if not self.bundles_to_accounts[old_bundle_id]:
            del self.bundles_to_accounts[old_bundle_id]

        if new_bundle_id not in self.bundles_to_accounts:
            self.bundles_to_accounts[new_bundle_id] = set()

        self.bundles_to_accounts[new_bundle_id].add(account_id)


    def add_action(self, action):
        action.set_storage(self)

        if action.saved_meta_action is not None:

            meta_action_uid = action.saved_meta_action.uid

            if meta_action_uid not in self.meta_actions_to_actions:
                self.meta_actions_to_actions[meta_action_uid] = set()
            self.meta_actions_to_actions[meta_action_uid].add(self.get_action_uid(action))

            if meta_action_uid not in self.meta_actions:
                self.meta_actions[meta_action_uid] = action.saved_meta_action
                action.meta_action.set_storage(self)

    def remove_action(self, action):
        action.set_storage(None)
        last_action = action.hero.actions.current_action
        if last_action is not action:
            raise exceptions.RemoveActionFromMiddleError(action=action, last_action=last_action, actions_list=action.hero.actions.actions_list)

        if action.meta_action is not None:

            meta_action_uid = action.saved_meta_action.uid

            self.meta_actions_to_actions[meta_action_uid].remove(self.get_action_uid(action))

            if not self.meta_actions_to_actions[meta_action_uid]:
                del self.meta_actions_to_actions[meta_action_uid]
                del self.meta_actions[meta_action_uid]

    @classmethod
    def get_action_uid(cls, action):
        number = action.hero.actions.number
        return (action.hero.id, number - 1 if action is action.hero.actions.current_action else number)

    def on_highlevel_data_updated(self):
        for hero in self.heroes.values():
            hero.on_highlevel_data_updated()


    @contextlib.contextmanager
    def on_exception(self, logger, message, data, excluded_bundle_id):
        try:
            yield
        except Exception:
            if project_settings.TESTS_RUNNING:
                raise

            if logger:
                logger.error(message % data)
                logger.error('Exception',
                             exc_info=sys.exc_info(),
                             extra={} )

            self.ignored_bundles.add(excluded_bundle_id)

            self._save_on_exception()

            if logger:
                logger.error('bundles saved')


    # this method can be colled outside of process_turn
    # for example from help ability
    def process_turn__single_hero(self, hero, logger, continue_steps_if_needed):
        leader_action = hero.actions.current_action
        bundle_id = leader_action.bundle_id

        if bundle_id in self.ignored_bundles:
            return

        with self.on_exception(logger,
                               message='LogicStorage.process_turn catch exception, while processing hero %d, try to save all bundles except %d',
                               data=(hero.id, bundle_id),
                               excluded_bundle_id=bundle_id):

            while True:
                leader_action.process_turn()

                # process new actions if it has been created or remove already processed actions
                if (continue_steps_if_needed and
                    leader_action != hero.actions.current_action and
                    hero.actions.current_action.APPROVED_FOR_STEPS_CHAIN and
                    leader_action.APPROVED_FOR_STEPS_CHAIN):

                    leader_action = hero.actions.current_action
                    continue

                break


            hero.process_rare_operations()

        if leader_action.removed and leader_action.bundle_id != hero.actions.current_action.bundle_id:
            self.unmerge_bundles(account_id=hero.account_id,
                                 old_bundle_id=leader_action.bundle_id,
                                 new_bundle_id=hero.actions.current_action.bundle_id)
            self.skipped_heroes.add(hero.id)


    def process_turn(self, logger=None, continue_steps_if_needed=True):
        self.switch_caches()

        timestamp = time.time()

        turn_number = TimePrototype.get_current_turn_number()

        processed_heroes = 0

        for hero in self.heroes.values():
            if hero.actions.current_action.bundle_id in self.ignored_bundles:
                continue

            if hero.id in self.skipped_heroes:
                continue

            if not hero.can_process_turn(turn_number):
                continue

            self.process_turn__single_hero(hero=hero, logger=logger, continue_steps_if_needed=continue_steps_if_needed)

            processed_heroes += 1

            if conf.game_settings.UNLOAD_OBJECTS:
                hero.unload_serializable_items(timestamp)

        if logger:
            logger.info('[next_turn] processed heroes: %d / %d' % (processed_heroes, len(self.heroes)))
            if self.ignored_bundles:
                logger.info('[next_turn] ignore bundles: %r' % list(self.ignored_bundles))

    def _save_on_exception(self):
        for hero_id, hero in self.heroes.iteritems():
            if hero.actions.current_action.bundle_id in self.ignored_bundles:
                continue

            time_border = datetime.datetime.now() - datetime.timedelta(seconds=conf.game_settings.SAVE_ON_EXCEPTION_TIMEOUT)

            if hero.saved_at < time_border:
                self._save_hero_data(hero_id)

    def save_all(self, logger=None):
        heroes = self.heroes.items()
        heroes.sort(key=lambda x: x[0])

        for hero_id, hero in heroes:

            if hero.actions.current_action.bundle_id in self.ignored_bundles:
                continue

            if logger:
                logger.info('save hero %d' % hero_id)
            self._save_hero_data(hero_id)

    def _get_bundles_to_save(self):
        bundles = set()

        if heroes_settings.DUMP_CACHED_HEROES:
            bundles |= self._get_bundles_to_cache()

        unsaved_heroes = sorted(self.heroes.itervalues(), key=lambda h: h.saved_at)

        saved_uncached_heroes_number = int(conf.game_settings.SAVED_UNCACHED_HEROES_FRACTION * len(self.heroes) + 1)

        bundles.update(hero.actions.current_action.bundle_id for hero in unsaved_heroes[:saved_uncached_heroes_number])

        for hero in self.heroes.itervalues():
            if hero.force_save_required:
                hero.force_save_required = False
                bundles.add(hero.actions.current_action.bundle_id)

        return bundles

    def _get_bundles_to_cache(self):
        return set(hero.actions.current_action.bundle_id
                   for hero in self.heroes.itervalues()
                   if hero.is_ui_caching_required)

    def save_changed_data(self, logger=None):
        saved_bundles = self._get_bundles_to_save()
        cached_bundles = self._get_bundles_to_cache()

        if logger:
            logger.info('[save_changed_data] saved bundles number: %d' % len(saved_bundles))

        for hero_id, hero in self.heroes.iteritems():

            bundle_id = hero.actions.current_action.bundle_id

            if bundle_id in self.ignored_bundles:
                continue

            if bundle_id in cached_bundles:
                self.cache_queue.add(hero_id)

            if bundle_id in saved_bundles:
                self._save_hero_data(hero_id)

        cached_heroes_number = self.process_cache_queue(update_cache=True)

        if logger:
            logger.info('[save_changed_data] cached heroes: %d' % cached_heroes_number)


    def process_cache_queue(self, update_cache=False):
        to_cache = {}

        for hero_id in self.cache_queue:
            hero = self.heroes[hero_id]
            cache_key = hero.cached_ui_info_key
            to_cache[cache_key] = hero.ui_info(actual_guaranteed=True, old_info=self.previous_cache.get(cache_key))

        cache.set_many(to_cache, heroes_settings.UI_CACHING_TIMEOUT)

        self.cache_queue.clear()

        if update_cache:
            self.current_cache.update(to_cache)

        return len(to_cache)


    def switch_caches(self):
        self.previous_cache = self.current_cache
        self.current_cache = {}

    def _test_save(self):
        for hero_id in self.heroes:
            self._save_hero_data(hero_id)

        test_storage = LogicStorage()
        for hero_id in self.heroes:
            test_storage._add_hero(heroes_logic.load_hero(hero_id=hero_id))

        return self == test_storage

    def __eq__(self, other):
        return (self.heroes == other.heroes and
                self.accounts_to_heroes == other.accounts_to_heroes)
