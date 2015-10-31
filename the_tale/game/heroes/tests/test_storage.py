# coding: utf-8
import datetime
import time
import random
import copy

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype, GameState

from the_tale.game.quests.relations import QUESTS

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Damage

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.map.places import storage as places_storage
from the_tale.game.map.places.relations import CITY_MODIFIERS
from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.relations import HABIT_PEACEFULNESS_INTERVAL, HABIT_HONOR_INTERVAL

from the_tale.game.heroes.habilities import ABILITY_TYPE, ABILITIES, battle, ABILITY_AVAILABILITY
from the_tale.game.heroes.conf import heroes_settings
from the_tale.game.heroes import relations
from the_tale.game.heroes import messages
from the_tale.game.heroes import storage


class PositionDescriptionsStorageTests(testcase.TestCase):

    def setUp(self):
        super(PositionDescriptionsStorageTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        storage.position_descriptions.clear()

    def test_clear(self):
        self.assertEqual(storage.position_descriptions._position_in_place_cache, {})
        self.assertEqual(storage.position_descriptions._position_near_place_cache, {})
        self.assertEqual(storage.position_descriptions._position_on_road_cache, {})
        self.assertEqual(storage.position_descriptions._actual_places_version, places_storage.places_storage._version)

    def test_sync(self):
        with mock.patch('the_tale.game.heroes.storage.PositionDescriptionsStorage.clear') as clear:
            storage.position_descriptions.sync()

        self.assertEqual(clear.call_count, 0)

        places_storage.places_storage.update_version()

        with mock.patch('the_tale.game.heroes.storage.PositionDescriptionsStorage.clear') as clear:
            storage.position_descriptions.sync()

        self.assertEqual(clear.call_count, 1)

    def test_text_in_place(self):
        text = storage.position_descriptions.text_in_place(self.place_1.id)
        self.assertTrue(text)
        self.assertEqual(storage.position_descriptions._position_in_place_cache, {self.place_1.id: text})

    def test_text_near_place(self):
        text = storage.position_descriptions.text_near_place(self.place_1.id)
        self.assertTrue(text)
        self.assertEqual(storage.position_descriptions._position_near_place_cache, {self.place_1.id: text})

    def test_text_on_road(self):
        text = storage.position_descriptions.text_on_road(self.place_1.id, self.place_2.id)
        self.assertTrue(text)
        self.assertEqual(storage.position_descriptions._position_on_road_cache, {(self.place_1.id, self.place_2.id): text})

    def text_in_wild_lands(self, place_id):
        self.assertEqual(storage.position_descriptions.text_in_wild_lands(), u'дикие земли')
