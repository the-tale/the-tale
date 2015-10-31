# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map


from the_tale.game.logic_storage import LogicStorage

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage



class HeroPositionTest(testcase.TestCase):

    def setUp(self):
        super(HeroPositionTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.road_1_2 = roads_storage.get_by_places(self.place_1, self.place_2)
        self.road_2_3 = roads_storage.get_by_places(self.place_2, self.place_3)

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.safety', 1.0)
    def test_is_battle_start_needed__safety(self):
        self.assertTrue(all(not self.hero.is_battle_start_needed() for i in xrange(100)))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.safety', 0.0)
    @mock.patch('the_tale.game.balance.constants.MAX_BATTLES_PER_TURN', 1.0)
    def test_is_battle_start_needed__no_safety(self):
        self.assertTrue(all(self.hero.is_battle_start_needed() for i in xrange(100)))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.safety', 0.5)
    @mock.patch('the_tale.game.heroes.objects.Hero.battles_per_turn_summand', 0.5)
    @mock.patch('the_tale.game.balance.constants.MAX_BATTLES_PER_TURN', 1.0)
    def test_is_battle_start_needed__hero_modifier(self):
        self.assertTrue(all(self.hero.is_battle_start_needed() for i in xrange(100)))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.safety', 0.5)
    @mock.patch('the_tale.game.heroes.objects.Hero.battles_per_turn_summand', -0.5)
    @mock.patch('the_tale.game.balance.constants.MAX_BATTLES_PER_TURN', 1.0)
    def test_is_battle_start_needed__hero_modifier_2(self):
        self.assertTrue(all(not self.hero.is_battle_start_needed() for i in xrange(100)))

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.transport', 0.5)
    def test_modify_move_speed__less(self):
        self.assertEqual(self.hero.modify_move_speed(10), 5)

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.transport', 2.0)
    def test_modify_move_speed_greater(self):
        self.assertEqual(self.hero.modify_move_speed(10), 20.0)

    def test_get_neares_place(self):

        for place in places_storage.all():
            x, y = place.x, place.y

            with mock.patch('the_tale.game.heroes.position.Position.cell_coordinates', (x, y)):
                self.assertEqual(place.id, self.hero.position.get_nearest_place().id)


    def test_get_minumum_distance_to__check_map_structure(self):
        self.assertEqual(len(roads_storage.all()), 2)

    def test_get_minumum_distance_to__from_place(self):
        self.hero.position.set_place(self.place_1)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_1), 0)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_2), self.road_1_2.length)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_3), self.road_1_2.length + self.road_2_3.length)

    def test_get_minumum_distance_to__from_walking(self):
        self.hero.position.previous_place_id = self.place_1.id
        self.assertNotEqual(self.hero.position.previous_place, None)

        self.hero.position.set_coordinates(self.place_1.x, self.place_1.y, self.place_1.x, self.place_1.y - 1, 1.0)

        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_1), 1)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_2), 1 + self.road_1_2.length)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_3), 1 + self.road_1_2.length + self.road_2_3.length)

        self.assertEqual(self.hero.position.previous_place, None)  # test that when hero step outside town, previouse place will reset

    def test_get_minumum_distance_to__from_road(self):
        self.hero.position.previous_place_id = self.place_1.id
        self.assertNotEqual(self.hero.position.previous_place, None)

        self.hero.position.set_road(self.road_1_2, percents=0.25)

        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_1), self.road_1_2.length * 0.25)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_2), self.road_1_2.length * 0.75)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_3), self.road_1_2.length * 0.75 + self.road_2_3.length)

        self.assertEqual(self.hero.position.previous_place, None) # test that when hero step outside town, previouse place will reset

    def test_get_minumum_distance_to__from_road__invert(self):
        self.hero.position.set_road(self.road_1_2, percents=0.75)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_1), self.road_1_2.length * 0.75)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_2), self.road_1_2.length * 0.25)
        self.assertEqual(self.hero.position.get_minumum_distance_to(self.place_3), self.road_1_2.length * 0.25 + self.road_2_3.length)

    def test_get_position_on_map__place(self):
        self.hero.position.set_place(self.place_1)
        self.assertEqual(self.hero.position.get_position_on_map(), (self.place_1.x, self.place_1.y, 0, 0))

    def test_get_position_on_map__road(self):
        dx = self.place_1.x - self.place_2.x
        dy = self.place_1.y - self.place_2.y

        self.hero.position.set_road(self.road_1_2, percents=0)
        self.assertEqual(self.hero.position.get_position_on_map(), (self.place_1.x, self.place_1.y, dx, dy))

        self.hero.position.set_road(self.road_1_2, percents=1.0)
        self.assertEqual(self.hero.position.get_position_on_map(), (self.place_2.x, self.place_2.y, dx, dy))

        self.hero.position.set_road(self.road_1_2, percents=0.5)
        x, y, real_dx, real_dy = self.hero.position.get_position_on_map()
        self.assertTrue(self.place_1.x <= x <= self.place_2.x)
        self.assertTrue(self.place_1.y <= y <= self.place_2.y)
        self.assertEqual((real_dx, real_dy), (dx, dy))

    def test_get_position_on_map__road__inverted(self):
        dx = self.place_2.x - self.place_1.x
        dy = self.place_2.y - self.place_1.y

        self.hero.position.set_road(self.road_1_2, percents=0, invert=True)
        self.assertEqual(self.hero.position.get_position_on_map(), (self.place_2.x, self.place_2.y, dx, dy))

        self.hero.position.set_road(self.road_1_2, percents=1.0, invert=True)
        self.assertEqual(self.hero.position.get_position_on_map(), (self.place_1.x, self.place_1.y, dx, dy))

        self.hero.position.set_road(self.road_1_2, percents=0.5, invert=True)
        x, y, real_dx, real_dy = self.hero.position.get_position_on_map()
        self.assertTrue(self.place_1.x <= x <= self.place_2.x)
        self.assertTrue(self.place_1.y <= y <= self.place_2.y)
        self.assertEqual((real_dx, real_dy), (dx, dy))

    def test_get_position_on_map__walking(self):
        dx = 10 - 30
        dy = 40 - 20

        self.hero.position.set_coordinates(10, 40, 30, 20, 0.0)
        self.assertEqual(self.hero.position.get_position_on_map(), (10, 40, dx, dy))

        self.hero.position.set_coordinates(10, 40, 30, 20, 1.0)
        self.assertEqual(self.hero.position.get_position_on_map(), (30, 20, dx, dy))

        self.hero.position.set_coordinates(10, 40, 30, 20, 0.5)
        self.assertEqual(self.hero.position.get_position_on_map(), (20, 30, dx, dy))
