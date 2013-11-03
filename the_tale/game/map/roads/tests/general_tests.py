# coding: utf-8
from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.map.roads.models import Road, Waymark
from the_tale.game.map.roads.prototypes import RoadPrototype
from the_tale.game.map.roads.storage import roads_storage, waymarks_storage
from the_tale.game.map.roads.logic import update_waymarks


class GeneralTest(testcase.TestCase):

    def setUp(self):
        super(GeneralTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        self.r1 = roads_storage.get_by_places(self.p1, self.p2)
        self.r2 = roads_storage.get_by_places(self.p2, self.p3)

    def test_add_del_road(self):

        self.assertEqual(Road.objects.all().count(), 2)

        self.r2.exists = False
        self.r2.save()
        r3 = RoadPrototype.create(point_1=self.p1, point_2=self.p3)

        self.assertEqual(Road.objects.all().count(), 3)
        self.assertEqual(Road.objects.filter(exists=False).count(), 1)
        self.assertEqual(Road.objects.filter(exists=True).count(), 2)

        self.assertEqual(Waymark.objects.all().count(), 9)
        waymark = waymarks_storage.look_for_road(point_from=self.p1.id, point_to=self.p3.id)
        self.assertEqual(waymark.road.id, self.r1.id)

        update_waymarks()

        self.assertEqual(Waymark.objects.all().count(), 9)
        waymark = waymarks_storage.look_for_road(point_from=self.p1.id, point_to=self.p3.id)
        self.assertEqual(waymark.road.id, r3.id)

        self.assertNotEqual(r3.id, self.r1.id)

    def test_roll_road(self):
        self.assertEqual(RoadPrototype._roll(5, 4, 13, 8), 'rdrrdrrdrrdr')
        self.assertEqual(RoadPrototype._roll(13, 8, 5, 4), 'llullullullu')
        self.assertEqual(RoadPrototype._roll(5, 8, 13, 4), 'rrurrurrurru')
        self.assertEqual(RoadPrototype._roll(13, 4, 5, 8), 'ldlldlldlldl')

        self.assertEqual(RoadPrototype._roll(0, 4, 0, 8), 'dddd')
        self.assertEqual(RoadPrototype._roll(0, 8, 0, 4), 'uuuu')
        self.assertEqual(RoadPrototype._roll(5, 0, 13, 0), 'rrrrrrrr')
        self.assertEqual(RoadPrototype._roll(13, 0, 5, 0), 'llllllll')

        self.assertEqual(RoadPrototype._roll(5, 12, 3, 17), 'dlddldd')
