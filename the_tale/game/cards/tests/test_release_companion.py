# coding: utf-8
import random

from the_tale.common.utils import testcase

from the_tale.market import goods_types

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations

from the_tale.game.companions.tests import helpers as companions_helpers

from the_tale.game.cards.tests.helpers import CardsTestMixin




class ReleaseCompanionTests(CardsTestMixin):
    EFFECT = effects.ReleaseCompanion

    def setUp(self):
        super(ReleaseCompanionTests, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.effect = self.EFFECT()

        self.card = self.effect.create_card(available_for_auction=True)

        self.hero.cards.add_card(self.card)


    def test_use__has_companion(self):
        old_companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(old_companion_record))

        result, step, postsave_actions = self.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card_uid=self.card.uid))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.companion, None)


    def test_use__companion_exists(self):

        self.assertEqual(self.hero.companion, None)

        with self.check_not_changed(self.hero.cards.cards_count):
            result, step, postsave_actions = self.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card_uid=self.card.uid))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(self.hero.companion, None)
