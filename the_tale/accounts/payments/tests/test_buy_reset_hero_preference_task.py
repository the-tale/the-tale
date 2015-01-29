# coding: utf-8
import datetime
from the_tale.accounts.payments.postponed_tasks import BuyResetHeroPreference
from the_tale.accounts.payments.tests import base_buy_task

from the_tale.game.balance import enums as e
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.relations import ARCHETYPE

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.persons.storage import persons_storage
from the_tale.game.map.places.storage import places_storage
from the_tale.game.heroes.relations import PREFERENCE_TYPE, EQUIPMENT_SLOT, RISK_LEVEL, COMPANION_DEDICATION


def _create_reset_hero_preference_test(preference_type):

    class _BuyResetHeroPreferenceTaskTests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):
        PREFERENCE_TYPE = preference_type

        def setUp(self):
            super(_BuyResetHeroPreferenceTaskTests, self).setUp()

            self.task = BuyResetHeroPreference(account_id=self.account.id,
                                               preference_type=self.PREFERENCE_TYPE,
                                               transaction=self.transaction)

            self.storage = LogicStorage()
            self.storage.load_account_data(self.account)
            self.cmd_update_with_account_data__call_count = 0
            self.accounts_manages_worker = False
            self.supervisor_worker = True

            self.hero = self.storage.accounts_to_heroes[self.account.id]

            self.hero.preferences.set_mob(mobs_storage.all()[0])
            self.hero.preferences.set_place(places_storage.all()[0])
            self.hero.preferences.set_friend(persons_storage.all()[0])
            self.hero.preferences.set_enemy(persons_storage.all()[1])
            self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.HAND_PRIMARY)
            self.hero.preferences.set_favorite_item(EQUIPMENT_SLOT.HAND_PRIMARY)
            self.hero.preferences.set_risk_level(RISK_LEVEL.VERY_HIGH)
            self.hero.preferences.set_archetype(ARCHETYPE.MAGICAL)
            self.hero.preferences.set_companion_dedication(COMPANION_DEDICATION.EGOISM)
            self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE)

        def _get_expected_arguments(self):
            return {'preference_type': preference_type}

        def _check_not_used(self):
            self.assertNotEqual(self.hero.preferences.time_before_update(preference_type, datetime.datetime.now()), datetime.timedelta(seconds=0))

        def _check_used(self):
            self.assertEqual(self.hero.preferences.time_before_update(preference_type, datetime.datetime.now()), datetime.timedelta(seconds=0))

    _BuyResetHeroPreferenceTaskTests.__name__ = 'BuyResetHeroPreference_%s_TaskTests' % preference_type.name

    return _BuyResetHeroPreferenceTaskTests


for preference in PREFERENCE_TYPE.records:
    Class = _create_reset_hero_preference_test(preference)
    globals()[Class.__name__] = Class
