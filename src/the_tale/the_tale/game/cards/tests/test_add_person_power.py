
from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards
from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.politic_power import logic as politic_power_logic

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game import tt_api_impacts


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
            tt_api_impacts.debug_clear_service()
            card = self.CARD.effect.create_card(type=self.CARD,
                                                available_for_auction=True,
                                                direction=direction)

            person = self.place_1.persons[0]

            result, step, postsave_actions = card.effect.use(**self.use_attributes(hero=self.hero,
                                                                                   storage=self.storage,
                                                                                   value=person.id,
                                                                                   card=card))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

            impacts = politic_power_logic.get_last_power_impacts(limit=100)

            self.assertEqual(len(impacts), 1)

            self.assertEqual(impacts[0].amount, direction * self.CARD.effect.modificator)
            self.assertTrue(impacts[0].type.is_INNER_CIRCLE)
            self.assertTrue(impacts[0].target_type.is_PERSON)
            self.assertEqual(impacts[0].target_id, person.id)
            self.assertTrue(impacts[0].actor_type.is_HERO)
            self.assertEqual(impacts[0].actor_id, self.hero.id)

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
