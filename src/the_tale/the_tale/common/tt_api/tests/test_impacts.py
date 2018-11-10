
import smart_imports

smart_imports.all()


impacts_client = impacts.Client(entry_point=game_conf.settings.TT_IMPACTS_PERSONAL_ENTRY_POINT,
                                impact_type=game_tt_services.IMPACT_TYPE.FAME,
                                impact_class=game_tt_services.PowerImpact)


class ImpactsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        impacts_client.cmd_debug_clear_service()

        self.transaction_1 = uuid.uuid4()
        self.transaction_2 = uuid.uuid4()

        self.impacts = [game_tt_services.PowerImpact.hero_2_person(type=impacts_client.impact_type,
                                                                   hero_id=666,
                                                                   person_id=1,
                                                                   amount=100,
                                                                   turn=1,
                                                                   transaction=self.transaction_1),
                        game_tt_services.PowerImpact.hero_2_person(type=impacts_client.impact_type,
                                                                   hero_id=777,
                                                                   person_id=2,
                                                                   amount=-200,
                                                                   turn=1,
                                                                   transaction=self.transaction_1),
                        game_tt_services.PowerImpact.hero_2_person(type=impacts_client.impact_type,
                                                                   hero_id=777,
                                                                   person_id=1,
                                                                   amount=300,
                                                                   turn=2,
                                                                   transaction=self.transaction_2),
                        game_tt_services.PowerImpact.hero_2_place(type=impacts_client.impact_type,
                                                                  hero_id=888,
                                                                  place_id=2,
                                                                  amount=-400,
                                                                  turn=3,
                                                                  transaction=self.transaction_2)]

    def test_add_power_impacts(self):
        impacts_client.cmd_add_power_impacts(impacts=self.impacts[:2])

        impacts_client.cmd_add_power_impacts(impacts=self.impacts[2:])

        # add excluded impacts
        impacts_client.cmd_add_power_impacts(impacts=[game_tt_services.PowerImpact.hero_2_place(type=impacts_client.impact_type,
                                                                                                hero_id=888,
                                                                                                place_id=2,
                                                                                                amount=-0.5,
                                                                                                turn=3,
                                                                                                transaction=self.transaction_2),
                                                      game_tt_services.PowerImpact.hero_2_place(type=impacts_client.impact_type,
                                                                                                hero_id=888,
                                                                                                place_id=2,
                                                                                                amount=0.5,
                                                                                                turn=3,
                                                                                                transaction=self.transaction_2),
                                                      game_tt_services.PowerImpact.hero_2_place(type=impacts_client.impact_type,
                                                                                                hero_id=888,
                                                                                                place_id=2,
                                                                                                amount=0,
                                                                                                turn=3,
                                                                                                transaction=self.transaction_2)])

        last_impacts = impacts_client.cmd_get_last_power_impacts(limit=100)

        for impact in last_impacts:
            impact.time = None

        self.assertCountEqual(last_impacts, self.impacts)

    def test_get_last_power_impacts__limit(self):
        for impact in self.impacts:
            impacts_client.cmd_add_power_impacts(impacts=[impact])

        last_impacts = impacts_client.cmd_get_last_power_impacts(limit=3)

        for impact in last_impacts:
            impact.time = None

        self.assertCountEqual(last_impacts, self.impacts[1:])

    def test_get_last_power_impacts(self):
        for impact in self.impacts:
            impacts_client.cmd_add_power_impacts(impacts=[impact])

        last_impacts = impacts_client.cmd_get_last_power_impacts(limit=100)

        for impact in last_impacts:
            impact.time = None

        self.assertCountEqual(last_impacts, self.impacts)

    def test_get_last_power_impacts__actor_filter(self):
        for impact in self.impacts:
            impacts_client.cmd_add_power_impacts(impacts=[impact])

        last_impacts = impacts_client.cmd_get_last_power_impacts(limit=100,
                                                                 actor_type=impacts.OBJECT_TYPE.HERO,
                                                                 actor_id=777)

        for impact in last_impacts:
            impact.time = None

        self.assertCountEqual(last_impacts, [self.impacts[1], self.impacts[2]])

    def test_get_last_power_impacts__target_filter(self):
        for impact in self.impacts:
            impacts_client.cmd_add_power_impacts(impacts=[impact])

        last_impacts = impacts_client.cmd_get_last_power_impacts(limit=100,
                                                                 target_type=impacts.OBJECT_TYPE.PERSON,
                                                                 target_id=1)

        for impact in last_impacts:
            impact.time = None

        self.assertCountEqual(last_impacts, [self.impacts[0], self.impacts[2]])

    def test_get_last_power_impacts__actor_target_filter(self):
        for impact in self.impacts:
            impacts_client.cmd_add_power_impacts(impacts=[impact])

        last_impacts = impacts_client.cmd_get_last_power_impacts(limit=100,
                                                                 actor_type=impacts.OBJECT_TYPE.HERO,
                                                                 actor_id=777,
                                                                 target_type=impacts.OBJECT_TYPE.PERSON,
                                                                 target_id=1)

        for impact in last_impacts:
            impact.time = None

        self.assertCountEqual(last_impacts, [self.impacts[2]])

    def test_get_targets_impacts(self):
        impacts_client.cmd_add_power_impacts(impacts=self.impacts)

        last_impacts = impacts_client.cmd_get_targets_impacts(targets=[(impacts.OBJECT_TYPE.PERSON, 1),
                                                                       (impacts.OBJECT_TYPE.PLACE, 2)])

        self.assertCountEqual(last_impacts,
                              [game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=None,
                                                            actor_id=None,
                                                            target_type=impacts.OBJECT_TYPE.PERSON,
                                                            target_id=1,
                                                            amount=400),
                               game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=None,
                                                            actor_id=None,
                                                            target_type=impacts.OBJECT_TYPE.PLACE,
                                                            target_id=2,
                                                            amount=-400)])

    def test_get_actor_impacts(self):
        impacts_client.cmd_add_power_impacts(impacts=self.impacts)

        last_impacts = impacts_client.cmd_get_actor_impacts(actor_type=impacts.OBJECT_TYPE.HERO,
                                                            actor_id=777,
                                                            target_types=[impacts.OBJECT_TYPE.PERSON])

        self.assertCountEqual(last_impacts,
                              [game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=impacts.OBJECT_TYPE.HERO,
                                                            actor_id=777,
                                                            target_type=impacts.OBJECT_TYPE.PERSON,
                                                            target_id=2,
                                                            amount=-200),
                               game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=impacts.OBJECT_TYPE.HERO,
                                                            actor_id=777,
                                                            target_type=impacts.OBJECT_TYPE.PERSON,
                                                            target_id=1,
                                                            amount=300)])

    def test_get_impacters_ratings(self):
        impacts_client.cmd_add_power_impacts(impacts=self.impacts)

        ratings = impacts_client.cmd_get_impacters_ratings(targets=[(impacts.OBJECT_TYPE.PERSON, 1),
                                                                    (impacts.OBJECT_TYPE.PLACE, 2),
                                                                    (impacts.OBJECT_TYPE.PLACE, 3124)],
                                                           actor_types=[impacts.OBJECT_TYPE.HERO],
                                                           limit=100)

        self.assertCountEqual(ratings.keys(), [(impacts.OBJECT_TYPE.PERSON, 1),
                                               (impacts.OBJECT_TYPE.PLACE, 2),
                                               (impacts.OBJECT_TYPE.PLACE, 3124)])

        self.assertEqual(ratings[(impacts.OBJECT_TYPE.PERSON, 1)],
                         [game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                       actor_type=impacts.OBJECT_TYPE.HERO,
                                                       actor_id=777,
                                                       target_type=impacts.OBJECT_TYPE.PERSON,
                                                       target_id=1,
                                                       amount=300),
                          game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                       actor_type=impacts.OBJECT_TYPE.HERO,
                                                       actor_id=666,
                                                       target_type=impacts.OBJECT_TYPE.PERSON,
                                                       target_id=1,
                                                       amount=100)])

    def test_scale_impacts(self):
        impacts_client.cmd_add_power_impacts(impacts=self.impacts)

        scale = 1.5

        impacts_client.cmd_scale_impacts(target_types=[impacts.OBJECT_TYPE.PERSON],
                                         scale=scale)

        last_impacts = impacts_client.cmd_get_targets_impacts(targets=[(impacts.OBJECT_TYPE.PERSON, 1),
                                                                       (impacts.OBJECT_TYPE.PERSON, 2),
                                                                       (impacts.OBJECT_TYPE.PLACE, 2)])

        self.assertCountEqual(last_impacts,
                              [game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=None,
                                                            actor_id=None,
                                                            target_type=impacts.OBJECT_TYPE.PERSON,
                                                            target_id=1,
                                                            amount=400 * scale),
                               game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=None,
                                                            actor_id=None,
                                                            target_type=impacts.OBJECT_TYPE.PERSON,
                                                            target_id=2,
                                                            amount=-200 * scale),
                               game_tt_services.PowerImpact(type=impacts_client.impact_type,
                                                            actor_type=None,
                                                            actor_id=None,
                                                            target_type=impacts.OBJECT_TYPE.PLACE,
                                                            target_id=2,
                                                            amount=-400)])
