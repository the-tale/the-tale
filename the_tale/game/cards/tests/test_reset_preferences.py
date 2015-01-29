# coding: utf-8
import datetime

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin
from the_tale.game.heroes.relations import PREFERENCE_TYPE


class ResetPreferenceCommon(testcase.TestCase):

    def setUp(self):
        super(ResetPreferenceCommon, self).setUp()

    def test_one_card_for_one_preference(self):
        preferences = list()

        for card in effects.EFFECTS.values():
            if hasattr(card, 'PREFERENCE'):
                preferences.append(card.PREFERENCE)

        self.assertEqual(len(preferences), len(PREFERENCE_TYPE.records))
        self.assertEqual(set(preferences), set(PREFERENCE_TYPE.records))


class ResetPreferenceMinix(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(ResetPreferenceMinix, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero.preferences._set(self.CARD.PREFERENCE, self.hero.preferences._get(self.CARD.PREFERENCE))

        self.card = self.CARD()

    @mock.patch('the_tale.game.heroes.preferences.HeroPreferences.is_available', lambda self, preference_type, account: True)
    def test_use(self):
        self.assertFalse(self.hero.preferences.can_update(self.CARD.PREFERENCE, datetime.datetime.now()))

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.preferences.can_update(self.CARD.PREFERENCE, datetime.datetime.now()))


    @mock.patch('the_tale.game.heroes.preferences.HeroPreferences.is_available', lambda self, preference_type, account: False)
    def test_not_available(self):
        self.assertFalse(self.hero.preferences.can_update(self.CARD.PREFERENCE, datetime.datetime.now()))

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertFalse(self.hero.preferences.can_update(self.CARD.PREFERENCE, datetime.datetime.now()))


class ResetPreferenceMobTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetMob

class ResetPreferencePlaceTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetPlace

class ResetPreferenceFriendTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetFriend

class ResetPreferenceEnemyTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetEnemy

class ResetPreferenceEnergyRegenerationTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetEnergyRegeneration

class ResetPreferenceEquipmentSlotTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetEquipmentSlot

class ResetPreferenceRiskLevelTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetRiskLevel

class ResetPreferenceFavoriteItemTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetFavoriteItem

class ResetPreferenceArchetypeTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetArchetype

class ResetPreferenceCompanionDedicationTests(ResetPreferenceMinix, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetCompanionDedication


class ResetPreferenceAllTests(CardsTestMixin, testcase.TestCase):
    CARD = effects.PreferencesCooldownsResetAll

    def setUp(self):
        super(ResetPreferenceAllTests, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        for preference in PREFERENCE_TYPE.records:
            self.hero.preferences._set(preference, self.hero.preferences._get(preference))

        self.card = self.CARD()

    def test_use(self):
        for preference in PREFERENCE_TYPE.records:
            self.assertFalse(self.hero.preferences.can_update(preference, datetime.datetime.now()))

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        for preference in PREFERENCE_TYPE.records:
            self.assertTrue(self.hero.preferences.can_update(preference, datetime.datetime.now()))
