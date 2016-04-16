# coding: utf-8

import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects
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

        self.card = self.CARD()

        environment.deinitialize()
        environment.initialize()

        self.highlevel = environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')


    def test_use(self):

        person = self.place_1.persons[0]

        result, step, postsave_actions = self.card.use(**self.use_attributes(hero=self.hero, storage=self.storage, person_id=person.id))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        with mock.patch('the_tale.game.persons.logic.PersonPoliticPower.change_power') as change_power:
            result, step, postsave_actions = self.card.use(**self.use_attributes(hero=self.hero,
                                                                                 step=step,
                                                                                 highlevel=self.highlevel,
                                                                                 person_id=person.id))
        self.assertEqual(change_power.call_args_list,
                         [mock.call(hero_id=self.hero.id, person=person, power=self.CARD.BONUS, has_in_preferences=True)])

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_no_person(self):
        self.assertEqual(self.card.use(**self.use_attributes(hero=self.hero, person_id=666, storage=self.storage)),
                        (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class AddPersonPowerPositiveCommon(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerPositiveCommon

class AddPersonPowerPositiveUncommon(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerPositiveUncommon

class AddPersonPowerPositiveRare(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerPositiveRare

class AddPersonPowerPositiveEpic(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerPositiveEpic

class AddPersonPowerPositiveLegendary(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerPositiveLegendary


class AddPersonPowerNegativeCommon(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerNegativeCommon

class AddPersonPowerNegativeUncommon(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerNegativeUncommon

class AddPersonPowerNegativeRare(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerNegativeRare

class AddPersonPowerNegativeEpic(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerNegativeEpic

class AddPersonPowerNegativeLegendary(AddPersonPowerMixin, testcase.TestCase):
    CARD = effects.AddPersonPowerNegativeLegendary
