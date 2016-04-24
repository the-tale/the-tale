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

from the_tale.game.persons import relations


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

    def test_place_effects__economic_and_specialization(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.TRUTH_SEEKER
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.MULTIWISE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertEqual(place_attributes,
                         set((places_relations.ATTRIBUTE.PRODUCTION,
                              places_relations.ATTRIBUTE.SAFETY,
                              places_relations.ATTRIBUTE.TRANSPORT,
                              places_relations.ATTRIBUTE.FREEDOM,
                              places_relations.ATTRIBUTE.STABILITY,

                              places_relations.ATTRIBUTE.MODIFIER_TRANSPORT_NODE,
                              places_relations.ATTRIBUTE.MODIFIER_OUTLAWS,
                              places_relations.ATTRIBUTE.MODIFIER_HOLY_CITY,
                              places_relations.ATTRIBUTE.MODIFIER_CRAFT_CENTER,
                              places_relations.ATTRIBUTE.MODIFIER_FORT,
                              places_relations.ATTRIBUTE.MODIFIER_POLITICAL_CENTER,
                              places_relations.ATTRIBUTE.MODIFIER_TRADE_CENTER,
                              places_relations.ATTRIBUTE.MODIFIER_POLIC,
                              places_relations.ATTRIBUTE.MODIFIER_RESORT)))


    def test_place_effects__terrain_radius_bonus(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.FIDGET
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.MULTIWISE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertIn(places_relations.ATTRIBUTE.TERRAIN_RADIUS, place_attributes)


    def test_place_effects__politic_radius_bonus(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.TRUTH_SEEKER
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.ACTIVE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertIn(places_relations.ATTRIBUTE.POLITIC_RADIUS, place_attributes)


    def test_place_effects__stability_renewing_bonus(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.TRUTH_SEEKER
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.RELIABLE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertIn(places_relations.ATTRIBUTE.STABILITY_RENEWING_SPEED, place_attributes)


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


    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities(self):
        self.person.attrs.job_group_priority = {}
        self.assertEqual(self.person.job_effects_priorities(),
                         {jobs_effects.EFFECT.PLACE_PRODUCTION: 1.0,
                          jobs_effects.EFFECT.PLACE_SAFETY: 0.6,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.2,
                          jobs_effects.EFFECT.HERO_MONEY: 0.3,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 0.3,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 0.3,
                          jobs_effects.EFFECT.HERO_ENERGY: 0.3})

    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities__job_group_priorities(self):
        self.person.attrs.job_group_priority = {jobs_effects.EFFECT_GROUP.ON_PLACE: 0.5,
                                                jobs_effects.EFFECT_GROUP.ON_HEROES: 1.5}
        self.assertEqual(self.person.job_effects_priorities(),
                         {jobs_effects.EFFECT.PLACE_PRODUCTION: 1.5,
                          jobs_effects.EFFECT.PLACE_SAFETY: 1.1,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.7,
                          jobs_effects.EFFECT.PLACE_TRANSPORT: 0.09999999999999998,
                          jobs_effects.EFFECT.PLACE_FREEDOM: 0.5,
                          jobs_effects.EFFECT.HERO_MONEY: 1.8,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 1.8,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 1.8,
                          jobs_effects.EFFECT.HERO_ENERGY: 1.8})


    @mock.patch('the_tale.game.persons.objects.Person.total_politic_power_fraction', 0.5)
    def test_get_job_power(self):
        self.person.attrs.job_power_bonus = 0
        self.assertEqual(self.person.get_job_power(), 2.0)

    @mock.patch('the_tale.game.persons.objects.Person.total_politic_power_fraction', 0.5)
    def test_get_job_power__power_bonus(self):
        self.person.attrs.job_power_bonus = 10
        self.assertEqual(self.person.get_job_power(), 12.0)


    def test_give_job_power(self):

        with self.check_not_changed(lambda: self.person.job.effect):
            with mock.patch('the_tale.game.jobs.effects.BaseEffect.apply_to_heroes') as apply_to_heroes:
                self.person.job.give_power(1)
                self.assertEqual(self.person.update_job(), ())

        self.assertEqual(apply_to_heroes.call_count, 0)

        with self.check_changed(lambda: self.person.job.effect):
            with mock.patch('the_tale.game.jobs.effects.BaseEffect.apply_to_heroes', mock.Mock(return_value=(1, 2))) as apply_to_heroes:
                self.person.job.give_power(1000000000)
                self.assertEqual(self.person.update_job(), (1, 2))

        self.assertEqual(apply_to_heroes.call_count, 1)
