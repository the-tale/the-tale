
import smart_imports

smart_imports.all()


FAKE_ECONOMIC = {places_relations.ATTRIBUTE.PRODUCTION: 1.0,
                 places_relations.ATTRIBUTE.FREEDOM: 0,
                 places_relations.ATTRIBUTE.SAFETY: 0.6,
                 places_relations.ATTRIBUTE.TRANSPORT: -0.4,
                 places_relations.ATTRIBUTE.STABILITY: 0.2,
                 places_relations.ATTRIBUTE.CULTURE: 0.7}


class PersonJobTests(utils_testcase.TestCase):

    def setUp(self):
        super(PersonJobTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.person = self.place_1.persons[0]

        game_tt_services.debug_clear_service()

        self.job = jobs_logic.create_job(jobs.PersonJob)

    def test_static_values(self):
        self.assertEqual(self.job.ACTOR, 'person')
        self.assertTrue(self.job.ACTOR_TYPE.is_PERSON)
        self.assertTrue(self.job.POSITIVE_TARGET_TYPE.is_JOB_PERSON_POSITIVE)
        self.assertTrue(self.job.NEGATIVE_TARGET_TYPE.is_JOB_PERSON_NEGATIVE)
        self.assertEqual(self.job.NORMAL_POWER,
                         jobs_logic.normal_job_power(politic_power_conf.settings.PERSON_INNER_CIRCLE_SIZE))

    def test_load_power(self):
        with mock.patch('the_tale.game.politic_power.logic.get_job_power', mock.Mock(return_value=666)) as get_job_power:
            self.assertEqual(self.job.load_power(self.person.id), 666)

        get_job_power.assert_called_once_with(person_id=self.person.id)

    def test_load_inner_circle(self):
        with mock.patch('the_tale.game.politic_power.logic.get_inner_circle', mock.Mock(return_value=666)) as get_inner_circle:
            self.assertEqual(self.job.load_inner_circle(self.person.id), 666)

        get_inner_circle.assert_called_once_with(person_id=self.person.id)

    def test_get_job_power(self):
        with mock.patch('the_tale.game.politic_power.storage.PowerStorage.total_power_fraction',
                        lambda self, target_id: 0.5):
            self.person.attrs.job_power_bonus = 0
            self.assertEqual(self.job.get_job_power(self.person.id), 0.875)

    def test_get_job_power__power_bonus(self):
        with mock.patch('the_tale.game.politic_power.storage.PowerStorage.total_power_fraction',
                        lambda self, target_id: 0.5):
            self.person.attrs.job_power_bonus = 10
            self.assertEqual(self.job.get_job_power(self.person.id), 10.875)

    def test_get_project_name(self):
        name = self.person.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
        self.assertEqual(self.job.get_project_name(self.person.id), 'Проект Мастера {name}'.format(name=name))

    def test_get_objects(self):
        self.assertEqual(self.job.get_objects(self.person.id),
                         {'person': self.person,
                          'place': self.person.place})

    def test_get_group_priorities(self):
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.MULTIWISE
        self.person.refresh_attributes()

        priorities = jobs.get_group_priorities(self.person)

        self.assertEqual(priorities, {jobs_effects.EFFECT_GROUP.ON_HEROES: 1,
                                      jobs_effects.EFFECT_GROUP.ON_PLACE: 1})

    def test_get_group_priorities__bonus_for_place(self):
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.ENTERPRISING
        self.person.refresh_attributes()

        priorities = jobs.get_group_priorities(self.person)

        self.assertEqual(priorities, {jobs_effects.EFFECT_GROUP.ON_HEROES: 1,
                                      jobs_effects.EFFECT_GROUP.ON_PLACE: 2})

    def test_get_group_priorities_bonus_for_heroes(self):
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.ROMANTIC
        self.person.refresh_attributes()

        priorities = jobs.get_group_priorities(self.person)

        self.assertEqual(priorities, {jobs_effects.EFFECT_GROUP.ON_HEROES: 2,
                                      jobs_effects.EFFECT_GROUP.ON_PLACE: 1})

    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_get_raw_priorities(self):
        priorities = jobs.get_raw_priorities(self.person)

        self.assertEqual(priorities, {jobs_effects.EFFECT.PLACE_PRODUCTION: 2.0,
                                      jobs_effects.EFFECT.PLACE_SAFETY: 1.1,
                                      jobs_effects.EFFECT.PLACE_TRANSPORT: 0.09999999999999998,
                                      jobs_effects.EFFECT.PLACE_FREEDOM: 1,
                                      jobs_effects.EFFECT.PLACE_STABILITY: 0.45,
                                      jobs_effects.EFFECT.HERO_MONEY: 1,
                                      jobs_effects.EFFECT.HERO_ARTIFACT: 0.75,
                                      jobs_effects.EFFECT.HERO_EXPERIENCE: 1,
                                      jobs_effects.EFFECT.HERO_CARDS: 0.5,
                                      jobs_effects.EFFECT.PLACE_CULTURE: 1.7})

    def test_normalize_priorities(self):
        group_priorities = {jobs_effects.EFFECT_GROUP.ON_HEROES: 2,
                            jobs_effects.EFFECT_GROUP.ON_PLACE: 3}

        raw_priorities = {jobs_effects.EFFECT.PLACE_PRODUCTION: 2.0,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.5,
                          jobs_effects.EFFECT.HERO_MONEY: 1,
                          jobs_effects.EFFECT.HERO_CARDS: 1.5}

        priorities = jobs.normalize_priorities(group_priorities,
                                               raw_priorities)

        self.assertEqual(len(priorities), 4)
        self.assertAlmostEqual(sum(priority for effect, priority in priorities),
                               1)

        expected_priority = {jobs_effects.EFFECT.PLACE_PRODUCTION: 0.48,
                             jobs_effects.EFFECT.HERO_CARDS: 0.24,
                             jobs_effects.EFFECT.HERO_MONEY: 0.16,
                             jobs_effects.EFFECT.PLACE_STABILITY: 0.12}

        for effect, priority in priorities:
            self.assertAlmostEqual(priority, expected_priority[effect])

    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities(self):
        self.person.attrs.job_group_priority = {}
        self.assertEqual(self.person.job.get_effects_priorities(self.person.id),
                         {jobs_effects.EFFECT.PLACE_PRODUCTION: 0.15748031496062992,
                          jobs_effects.EFFECT.HERO_MONEY: 0.15384615384615385,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 0.15384615384615385,
                          jobs_effects.EFFECT.PLACE_CULTURE: 0.13385826771653542,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 0.11538461538461539,
                          jobs_effects.EFFECT.PLACE_SAFETY: 0.08661417322834646,
                          jobs_effects.EFFECT.PLACE_FREEDOM: 0.07874015748031496,
                          jobs_effects.EFFECT.HERO_CARDS: 0.07692307692307693,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.03543307086614173,
                          jobs_effects.EFFECT.PLACE_TRANSPORT: 0.007874015748031494})

    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities__job_group_priorities(self):
        self.person.attrs.job_group_priority = {jobs_effects.EFFECT_GROUP.ON_PLACE: 0.5,
                                                jobs_effects.EFFECT_GROUP.ON_HEROES: 1.5}

        self.assertEqual(self.person.job.get_effects_priorities(self.person.id),
                         {jobs_effects.EFFECT.HERO_MONEY: 0.19230769230769232,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 0.19230769230769232,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 0.14423076923076925,
                          jobs_effects.EFFECT.PLACE_PRODUCTION: 0.11811023622047244,
                          jobs_effects.EFFECT.PLACE_CULTURE: 0.10039370078740156,
                          jobs_effects.EFFECT.HERO_CARDS: 0.09615384615384616,
                          jobs_effects.EFFECT.PLACE_SAFETY: 0.06496062992125984,
                          jobs_effects.EFFECT.PLACE_FREEDOM: 0.05905511811023622,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.0265748031496063,
                          jobs_effects.EFFECT.PLACE_TRANSPORT: 0.00590551181102362})
