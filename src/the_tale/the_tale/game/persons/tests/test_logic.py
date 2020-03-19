
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_create_social_connection(self):
        connection_type = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_2.persons[0]

        if person_1.id < person_2.id:
            # swap to test sorting in tested function
            person_1, person_2 = person_2, person_1

        with self.check_delta(models.SocialConnection.objects.count, 1):
            with self.check_changed(lambda: storage.social_connections._version):
                connection = logic.create_social_connection(connection_type=connection_type, person_1=person_1, person_2=person_2)

        self.assertEqual(connection.connection, connection_type)

        self.assertTrue(connection.person_1_id < connection.person_2_id)

        self.assertEqual(connection.person_1_id, person_2.id)
        self.assertEqual(connection.person_2_id, person_1.id)

        self.assertIn(connection.id, storage.social_connections)

    def test_create_social_connection__uniqueness(self):
        connection = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_2.persons[0]

        logic.create_social_connection(connection_type=connection, person_1=person_1, person_2=person_2)

        self.assertRaises(exceptions.PersonsAlreadyConnectedError,
                          logic.create_social_connection, connection_type=connection, person_1=person_1, person_2=person_2)
        self.assertRaises(exceptions.PersonsAlreadyConnectedError,
                          logic.create_social_connection, connection_type=connection, person_1=person_2, person_2=person_1)
        self.assertRaises(exceptions.PersonsAlreadyConnectedError,
                          logic.create_social_connection, connection_type=relations.SOCIAL_CONNECTION_TYPE.random(exclude=(connection,)),
                          person_1=person_1, person_2=person_2)
        self.assertRaises(exceptions.PersonsAlreadyConnectedError,
                          logic.create_social_connection, connection_type=relations.SOCIAL_CONNECTION_TYPE.random(exclude=(connection,)),
                          person_1=person_2, person_2=person_1)

    def test_remove_social_connection(self):
        connection_type = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_2.persons[0]

        with self.check_delta(models.SocialConnection.objects.count, 1):
            with self.check_changed(lambda: storage.social_connections._version):
                connection = logic.create_social_connection(connection_type=connection_type, person_1=person_1, person_2=person_2)

        logic.remove_connection(connection)

        self.assertNotIn(connection.id, storage.social_connections)

    def test_move_person_to_place(self):
        person = self.place_1.persons[0]

        self.assertEqual(person.moved_at_turn, 0)

        game_turn.increment()
        game_turn.increment()
        game_turn.increment()

        with self.check_changed(lambda: storage.persons.version):
            logic.move_person_to_place(person, self.place_3)

        self.assertEqual(person.moved_at_turn, 3)
        self.assertEqual(person.place.id, self.place_3.id)


class TTPowerImpactsTests(utils_testcase.TestCase):

    def setUp(self):
        super(TTPowerImpactsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()
        self.person = self.place_1.persons[-1]

        self.actor_type = tt_api_impacts.OBJECT_TYPE.HERO
        self.actor_id = 666
        self.amount = 100500
        self.fame = 1000

        self.expected_power = round(self.person.place.attrs.freedom * self.amount)

    def test_person_inner_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.fame * self.person.attrs.places_help_amount)])

    def test_place_inner_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=False,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.fame * self.person.attrs.places_help_amount)])

    def test_inner_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.fame * self.person.attrs.places_help_amount)])

    def test_outer_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=False,
                                              place_inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.fame * self.person.attrs.places_help_amount)])

    def test_amount_below_zero(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=-self.amount,
                                              fame=0))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=-self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=-self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_NEGATIVE,
                                                            target_id=self.person.id,
                                                            amount=abs(self.expected_power)),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=-self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=-self.expected_power)])

    def test_has_building(self):
        places_logic.create_building(self.person, utg_name=game_names.generator().get_test_name())

        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount,
                                              fame=self.fame))

        multiplier = (1 + c.BUILDING_PERSON_POWER_BONUS)

        expected_power = round(self.person.place.attrs.freedom * self.amount * multiplier)

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                            target_id=self.person.id,
                                                            amount=expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                            target_id=self.person.id,
                                                            amount=expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.person.place.id,
                                                            amount=self.fame * self.person.attrs.places_help_amount)])


def fake_tt_power_impacts(**kwargs):
    yield kwargs


class ImpactsFromHeroTests(utils_testcase.TestCase):

    def setUp(self):
        super(ImpactsFromHeroTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()
        self.person = self.place_1.persons[-1]
        self.partner = self.place_2.persons[-1]
        self.concurrent = self.place_3.persons[-1]

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=self.account.id)

        self.amount = 100500
        self.fame = 1000

        self.expected_power = round(self.person.place.attrs.freedom * self.amount)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: False)
    def test_can_not_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 0,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'person': self.person,
                                             'person_inner_circle': False,
                                             'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    @mock.patch('the_tale.game.heroes.objects.Hero.modify_politics_power', lambda self, power, person: power * 0.75)
    def test_can_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 750,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'person': self.person,
                                             'person_inner_circle': False,
                                             'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_person_inner_circle(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.FRIEND, self.person)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'person': self.person,
                                             'person_inner_circle': True,
                                             'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_person_inner_circle__extended_inner_circle(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons={self.person.id},
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'person': self.person,
                                             'person_inner_circle': True,
                                             'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_place_inner_circle(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.place_1)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'person': self.person,
                                             'person_inner_circle': False,
                                             'place_inner_circle': True}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_place_inner_circle__extended_inner_circle(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places={self.place_1.id},
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'person': self.person,
                                             'person_inner_circle': False,
                                             'place_inner_circle': True}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: False)
    def test_social_connections__can_not_change_power(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))

        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 1000,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 100.0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 0,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: False)
    def test_social_connections__can_not_change_power__power_below_zero(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=-1000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))

        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 0,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 200,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_social_connections__can_change_power(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=10000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 10000,
                                                  'fame': 1000,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 1000,
                                                  'fame': 100.0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -2000,
                                                  'fame': 0,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_social_connections__person_inner_circles(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.FRIEND, self.person)

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=10000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 10000,
                                                  'fame': 1000,
                                                  'person': self.person,
                                                  'person_inner_circle': True,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 1000,
                                                  'fame': 100.0,
                                                  'person': self.partner,
                                                  'person_inner_circle': True,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -2000,
                                                  'fame': 0,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': True,
                                                  'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_social_connections__place_inner_circles(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.person.place)

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=10000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))

        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 10000,
                                                  'fame': 1000,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': True},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 1000,
                                                  'fame': 100.0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': True},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -2000,
                                                  'fame': 0,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': True}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_social_connections__place_inner_circles__power_below_zero(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.person.place)

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=-10000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))

        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -10000,
                                                  'fame': 0,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': True},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -1000,
                                                  'fame': 0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': True},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 2000,
                                                  'fame': 200,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': True}])

    def test_social_connections_between_frontier_and_core(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        self.person.place.is_frontier = True
        self.partner.place.is_frontier = False
        self.concurrent.place.is_frontier = True

        places_storage.places.save_all()

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=10000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))

        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 10000,
                                                  'fame': 1000,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 0,
                                                  'fame': 100.0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -2000,
                                                  'fame': 0,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_social_connections_between_core_and_frontier(self):
        self.person.attrs.social_relations_partners_power_modifier = 0.1
        self.person.attrs.social_relations_concurrents_power_modifier = 0.2

        self.person.place.is_frontier = False
        self.partner.place.is_frontier = False
        self.concurrent.place.is_frontier = True

        places_storage.places.save_all()

        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.CONCURRENT, self.person, self.concurrent)
        logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.PARTNER, self.person, self.partner)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        person=self.person,
                                                        power=10000,
                                                        inner_circle_places=set(),
                                                        inner_circle_persons=set(),
                                                        impacts_generator=fake_tt_power_impacts))

        self.assertCountEqual(impact_arguments, [{'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 10000,
                                                  'fame': 1000,
                                                  'person': self.person,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': 1000,
                                                  'fame': 100.0,
                                                  'person': self.partner,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False},
                                                 {'actor_id': self.hero.id,
                                                  'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                                  'amount': -2000,
                                                  'fame': 0,
                                                  'person': self.concurrent,
                                                  'person_inner_circle': False,
                                                  'place_inner_circle': False}])
