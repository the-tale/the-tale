import uuid
import random

from unittest import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks.prototypes import POSTPONED_TASK_LOGIC_RESULT, PostponedTaskPrototype
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game import names

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions import logic as companions_logic

from .. import cards
from .. import logic
from .. import tt_api
from .. import effects
from .. import objects
from .. import postponed_tasks

from the_tale.game.places import logic as places_logic


class UseCardTaskTests(testcase.TestCase):

    def setUp(self):
        super(UseCardTaskTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.building_1 = places_logic.create_building(person=self.place_1.persons[0], utg_name=names.generator().get_test_name('building-1-name'))

        environment.deinitialize()
        environment.initialize()

        self.highlevel = environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')

        self.task_data = {'place_id': self.place_1.id,
                          'person_id': self.place_1.persons[0].id,
                          'building_id': self.building_1.id}

        self.companion = companions_logic.create_random_companion_record('test-companion', state=companions_relations.STATE.ENABLED)


    def test_create(self):

        with mock.patch('the_tale.game.cards.effects.GetCompanion.get_available_companions', lambda x: [self.companion]):
            for card_type in cards.CARD.records:
                card = card_type.effect.create_card(card_type, available_for_auction=True)
                tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card])

                with self.check_delta(PostponedTaskPrototype._db_count, 1):
                    task = card.activate(self.hero, data=self.task_data)

                self.assertTrue(task.internal_logic.state.is_UNPROCESSED)


    def test_serialization(self):
        card = logic.create_card(allow_premium_cards=True, available_for_auction=True)
        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card])

        task = card.activate(self.hero, data=self.task_data).internal_logic

        self.assertEqual(task.serialize(), postponed_tasks.UseCardTask.deserialize(task.serialize()).serialize())

    def test_response_data(self):
        card = logic.create_card(allow_premium_cards=True, available_for_auction=True)
        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card])

        with mock.patch.object(card.type.effect.__class__, 'use', lambda *argv, **kwargs: (postponed_tasks.UseCardTask.RESULT.SUCCESSED, None, ())):
            task = card.activate(self.hero, data=self.task_data).internal_logic
            task.process(FakePostpondTaskPrototype(), self.storage)

        self.assertEqual(task.processed_data, {})

    def test_process_can_not_process(self):
        card = logic.create_card(allow_premium_cards=True, available_for_auction=True)

        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card])

        task = card.activate(self.hero, data=self.task_data).internal_logic

        with mock.patch.object(card.type.effect.__class__, 'use', lambda *argv, **kwargs: (postponed_tasks.UseCardTask.RESULT.FAILED, None, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(task.state, postponed_tasks.UseCardTask.STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        card = logic.create_card(allow_premium_cards=True, available_for_auction=True)
        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card])

        task = card.activate(self.hero, data=self.task_data).internal_logic

        with mock.patch.object(card.type.effect.__class__, 'use', lambda *argv, **kwargs: (postponed_tasks.UseCardTask.RESULT.SUCCESSED, None, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), storage=self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, postponed_tasks.UseCardTask.STATE.PROCESSED)

    def test_process_second_step_error(self):
        card = logic.create_card(allow_premium_cards=True, available_for_auction=True)
        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card])

        task = card.activate(self.hero, data=self.task_data).internal_logic

        with mock.patch.object(card.type.effect.__class__, 'use', lambda *argv, **kwargs: (postponed_tasks.UseCardTask.RESULT.CONTINUE, postponed_tasks.UseCardTask.STEP.HIGHLEVEL, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(task.step.is_HIGHLEVEL)
        self.assertEqual(task.state, postponed_tasks.UseCardTask.STATE.UNPROCESSED)

        with mock.patch.object(card.type.effect.__class__, 'use', lambda *argv, **kwargs: (postponed_tasks.UseCardTask.RESULT.FAILED, None, ())):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(task.state, postponed_tasks.UseCardTask.STATE.CAN_NOT_PROCESS)
