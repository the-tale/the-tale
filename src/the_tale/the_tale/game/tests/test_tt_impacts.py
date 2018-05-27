
import uuid
import random

from the_tale.common.utils import testcase

from .. import tt_api_impacts


class TTImpactsAPITests(testcase.TestCase):

    def setUp(self):
        super().setUp()
        tt_api_impacts.debug_clear_service()

        self.api = random.choice([tt_api_impacts.personal_impacts,
                                  tt_api_impacts.crowd_impacts,
                                  tt_api_impacts.job_impacts])

        self.transaction_1 = uuid.uuid4()
        self.transaction_2 = uuid.uuid4()

        self.impacts = [tt_api_impacts.PowerImpact.hero_2_person(type=self.api.impact_type,
                                                                 hero_id=666,
                                                                 person_id=1,
                                                                 amount=100,
                                                                 turn=1,
                                                                 transaction=self.transaction_1),
                        tt_api_impacts.PowerImpact.hero_2_person(type=self.api.impact_type,
                                                                 hero_id=777,
                                                                 person_id=2,
                                                                 amount=-200,
                                                                 turn=1,
                                                                 transaction=self.transaction_1),
                        tt_api_impacts.PowerImpact.hero_2_person(type=self.api.impact_type,
                                                                 hero_id=777,
                                                                 person_id=1,
                                                                 amount=300,
                                                                 turn=2,
                                                                 transaction=self.transaction_2),
                        tt_api_impacts.PowerImpact.hero_2_place(type=self.api.impact_type,
                                                                hero_id=888,
                                                                place_id=2,
                                                                amount=-400,
                                                                turn=3,
                                                                transaction=self.transaction_2)]

    def test_add_power_impacts(self):
        self.api.cmd_add_power_impacts(impacts=self.impacts[:2])

        self.api.cmd_add_power_impacts(impacts=self.impacts[2:])

        impacts = self.api.cmd_get_last_power_impacts(limit=100)

        for impact in impacts:
            impact.time = None

        self.assertCountEqual(impacts, self.impacts)

    def test_get_last_power_impacts__limit(self):
        for impact in self.impacts:
            self.api.cmd_add_power_impacts(impacts=[impact])

        impacts = self.api.cmd_get_last_power_impacts(limit=3)

        for impact in impacts:
            impact.time = None

        self.assertCountEqual(impacts, self.impacts[1:])

    def test_get_last_power_impacts(self):
        for impact in self.impacts:
            self.api.cmd_add_power_impacts(impacts=[impact])

        impacts = self.api.cmd_get_last_power_impacts(limit=100)

        for impact in impacts:
            impact.time = None

        self.assertCountEqual(impacts, self.impacts)

    def test_get_last_power_impacts__actor_filter(self):
        for impact in self.impacts:
            self.api.cmd_add_power_impacts(impacts=[impact])

        impacts = self.api.cmd_get_last_power_impacts(limit=100,
                                                      actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                      actor_id=777)

        for impact in impacts:
            impact.time = None

        self.assertCountEqual(impacts, [self.impacts[1], self.impacts[2]])

    def test_get_last_power_impacts__target_filter(self):
        for impact in self.impacts:
            self.api.cmd_add_power_impacts(impacts=[impact])

        impacts = self.api.cmd_get_last_power_impacts(limit=100,
                                                      target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                      target_id=1)

        for impact in impacts:
            impact.time = None

        self.assertCountEqual(impacts, [self.impacts[0], self.impacts[2]])

    def test_get_last_power_impacts__actor_target_filter(self):
        for impact in self.impacts:
            self.api.cmd_add_power_impacts(impacts=[impact])

        impacts = self.api.cmd_get_last_power_impacts(limit=100,
                                                      actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                      actor_id=777,
                                                      target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                      target_id=1)

        for impact in impacts:
            impact.time = None

        self.assertCountEqual(impacts, [self.impacts[2]])

    def test_get_targets_impacts(self):
        self.api.cmd_add_power_impacts(impacts=self.impacts)

        impacts = self.api.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PERSON, 1),
                                                            (tt_api_impacts.OBJECT_TYPE.PLACE, 2)])

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                          actor_type=None,
                                                          actor_id=None,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=1,
                                                          amount=400),
                               tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                          actor_type=None,
                                                          actor_id=None,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                          target_id=2,
                                                          amount=-400)])

    def test_get_impacters_ratings(self):
        self.api.cmd_add_power_impacts(impacts=self.impacts)

        ratings = self.api.cmd_get_impacters_ratings(targets=[(tt_api_impacts.OBJECT_TYPE.PERSON, 1),
                                                              (tt_api_impacts.OBJECT_TYPE.PLACE, 2),
                                                              (tt_api_impacts.OBJECT_TYPE.PLACE, 3124)],
                                                     actor_types=[tt_api_impacts.OBJECT_TYPE.HERO],
                                                     limit=100)

        self.assertCountEqual(ratings.keys(), [(tt_api_impacts.OBJECT_TYPE.PERSON, 1),
                                               (tt_api_impacts.OBJECT_TYPE.PLACE, 2),
                                               (tt_api_impacts.OBJECT_TYPE.PLACE, 3124)])

        self.assertEqual(ratings[(tt_api_impacts.OBJECT_TYPE.PERSON, 1)],
                         [tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                     actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                     actor_id=777,
                                                     target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                     target_id=1,
                                                     amount=300),
                          tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                     actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                     actor_id=666,
                                                     target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                     target_id=1,
                                                     amount=100)])

    def test_scale_impacts(self):
        self.api.cmd_add_power_impacts(impacts=self.impacts)

        scale = 1.5

        self.api.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.PERSON],
                                   scale=scale)

        impacts = self.api.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PERSON, 1),
                                                            (tt_api_impacts.OBJECT_TYPE.PERSON, 2),
                                                            (tt_api_impacts.OBJECT_TYPE.PLACE, 2)])

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                          actor_type=None,
                                                          actor_id=None,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=1,
                                                          amount=400*scale),
                               tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                          actor_type=None,
                                                          actor_id=None,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=2,
                                                          amount=-200*scale),
                               tt_api_impacts.PowerImpact(type=self.api.impact_type,
                                                          actor_type=None,
                                                          actor_id=None,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                          target_id=2,
                                                          amount=-400)])
