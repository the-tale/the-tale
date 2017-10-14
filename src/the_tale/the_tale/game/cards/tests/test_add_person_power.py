# coding: utf-8

from unittest import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards
from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.postponed_tasks import ComplexChangeTask


class AddPersonPowerMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddPersonPowerMixin, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        environment.deinitialize()
        environment.initialize()

        self.highlevel = environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')


    def test_use(self):
        for direction in (-1, 1):
            card = self.CARD.effect.create_card(type=self.CARD,
                                                available_for_auction=True,
                                                direction=direction)

            person = self.place_1.persons[0]

            result, step, postsave_actions = card.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, value=person.id, card=card))

            self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL))
            self.assertEqual(len(postsave_actions), 1)

            with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
                postsave_actions[0]()

            self.assertEqual(highlevel_logic_task_counter.call_count, 1)

            with mock.patch('the_tale.game.persons.logic.PersonPoliticPower.change_power') as change_power:
                result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                                            step=step,
                                                                                            highlevel=self.highlevel,
                                                                                            value=person.id,
                                                                                            card=card))
            self.assertEqual(change_power.call_args_list,
                             [mock.call(hero_id=self.hero.id, person=person, power=direction * self.CARD.effect.modificator, has_in_preferences=True)])

            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_no_person(self):
        for direction in (-1, 1):
            card = self.CARD.effect.create_card(type=self.CARD,
                                                available_for_auction=True,
                                                direction=direction)

            self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage, card=card)),
                            (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class AddPersonPowerCommon(AddPersonPowerMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_PERSON_POWER_COMMON

class AddPersonPowerUncommon(AddPersonPowerMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_PERSON_POWER_UNCOMMON

class AddPersonPowerRare(AddPersonPowerMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_PERSON_POWER_RARE

class AddPersonPowerEpic(AddPersonPowerMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_PERSON_POWER_EPIC

class AddPersonPowerLegendary(AddPersonPowerMixin, testcase.TestCase):
    CARD = cards.CARD.ADD_PERSON_POWER_LEGENDARY
