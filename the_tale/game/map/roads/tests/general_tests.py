# coding: utf-8
from django.test import TestCase

from game.logic import create_test_map

from game.map.roads.models import Road, Waymark
from game.map.roads.prototypes import RoadPrototype
from game.map.roads.storage import roads_storage, waymarks_storage
from game.map.roads.logic import update_waymarks

class GeneralTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        self.r1 = RoadPrototype.get_by_places(self.p1, self.p2)
        self.r2 = RoadPrototype.get_by_places(self.p2, self.p3)

        roads_storage.sync(force=True)
        waymarks_storage.sync(force=True)


    def test_add_del_road(self):

        self.assertEqual(Road.objects.all().count(), 2)

        self.r2.exists = False
        self.r2.save()
        r3 = RoadPrototype.create(point_1=self.p1, point_2=self.p3)

        roads_storage.sync(force=True)

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
