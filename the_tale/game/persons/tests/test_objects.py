# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.jobs import effects as jobs_effects

from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.places.prototypes import BuildingPrototype
from the_tale.game.places import relations as places_relations

from the_tale.game.persons.tests.helpers import create_person


class PersonTests(testcase.TestCase):

    def setUp(self):
        super(PersonTests, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.persons_changed_at_turn = TimePrototype.get_current_turn_number()

        self.p1, self.p2, self.p3 = create_test_map()

        self.person = create_person(self.p1)

        account = self.accounts_factory.create_account()
        self.hero_1 = heroes_logic.load_hero(account_id=account.id)

        account = self.accounts_factory.create_account()
        self.hero_2 = heroes_logic.load_hero(account_id=account.id)

        account = self.accounts_factory.create_account()
        self.hero_3 = heroes_logic.load_hero(account_id=account.id)

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()


    def test_initialize(self):
        self.assertEqual(self.person.place.persons_changed_at_turn, self.persons_changed_at_turn)

        self.assertEqual(self.person.friends_number, 0)
        self.assertEqual(self.person.enemies_number, 0)
        self.assertEqual(self.person.created_at_turn, TimePrototype.get_current_turn_number() - 1)

    def test_power_from_building(self):

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as change_person_power_call:
            self.person.cmd_change_power(hero_id=666, has_place_in_preferences=False, has_person_in_preferences=False, power=100)

        self.assertEqual(change_person_power_call.call_args, mock.call(hero_id=666,
                                                                       has_place_in_preferences=False,
                                                                       has_person_in_preferences=False,
                                                                       person_id=self.person.id,
                                                                       power_delta=100,
                                                                       place_id=None))

        BuildingPrototype.create(self.person, utg_name=names.generator.get_test_name('building-name'))

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as change_person_power_call:
            self.person.cmd_change_power(hero_id=666, has_place_in_preferences=False, has_person_in_preferences=False, power=-100)

        self.assertEqual(change_person_power_call.call_args, mock.call(hero_id=666,
                                                                       has_place_in_preferences=False,
                                                                       has_person_in_preferences=False,
                                                                       person_id=self.person.id,
                                                                       power_delta=-100,
                                                                       place_id=None))

FAKE_ECONOMIC = {places_relations.ATTRIBUTE.PRODUCTION: 1.0,
                 places_relations.ATTRIBUTE.FREEDOM: 0,
                 places_relations.ATTRIBUTE.SAFETY: 0.6,
                 places_relations.ATTRIBUTE.TRANSPORT: -0.4,
                 places_relations.ATTRIBUTE.STABILITY: 0.2}


class PersonJobsTests(testcase.TestCase):

    def setUp(self):
        super(PersonJobsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.person = create_person(self.place_1)


    @mock.patch('the_tale.game.persons.objects.Person.get_random_job_group', lambda person: jobs_effects.EFFECT_GROUP.ON_PLACE)
    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities__on_place(self):
        self.assertEqual(self.person.job_effects_priorities(),
                         {jobs_effects.EFFECT.PLACE_PRODUCTION: 1.0,
                          jobs_effects.EFFECT.PLACE_SAFETY: 0.6,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.2})


    @mock.patch('the_tale.game.persons.objects.Person.get_random_job_group', lambda person: jobs_effects.EFFECT_GROUP.ON_HEROES)
    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities__on_hero(self):
        self.assertEqual(self.person.job_effects_priorities(),
                         {jobs_effects.EFFECT.HERO_MONEY: 1.0,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 1.0,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 1.0,
                          jobs_effects.EFFECT.HERO_ENERGY: 1.0})


    @mock.patch('the_tale.game.persons.objects.Person.total_politic_power_fraction', 0.5)
    def test_get_job_power(self):
        self.assertEqual(self.person.get_job_power(), 2.0)


    def test_give_job_power(self):

        with self.check_not_changed(lambda: self.person.job.effect):
            with mock.patch('the_tale.game.jobs.effects.BaseEffect.apply_to_heroes') as apply_to_heroes:
                self.person.give_job_power(1)

        self.assertEqual(apply_to_heroes.call_count, 0)

        with self.check_changed(lambda: self.person.job.effect):
            with mock.patch('the_tale.game.jobs.effects.BaseEffect.apply_to_heroes') as apply_to_heroes:
                self.person.give_job_power(1000000000)

        self.assertEqual(apply_to_heroes.call_count, 1)
