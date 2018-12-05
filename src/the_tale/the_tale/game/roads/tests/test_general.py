
import smart_imports

smart_imports.all()


class GeneralTest(utils_testcase.TestCase):

    def setUp(self):
        super(GeneralTest, self).setUp()
        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.r1 = logic.road_between_places(self.p1, self.p2)
        self.r2 = logic.road_between_places(self.p2, self.p3)

    def test_add_del_road(self):

        self.assertEqual(models.Road.objects.all().count(), 2)

        self.r2.exists = False
        self.r2.save()
        r3 = prototypes.RoadPrototype.create(point_1=self.p1, point_2=self.p3)

        self.assertEqual(models.Road.objects.all().count(), 3)
        self.assertEqual(models.Road.objects.filter(exists=False).count(), 1)
        self.assertEqual(models.Road.objects.filter(exists=True).count(), 2)

        self.assertEqual(models.Waymark.objects.all().count(), 9)
        waymark = storage.waymarks.look_for_road(point_from=self.p1.id, point_to=self.p3.id)
        self.assertEqual(waymark.road.id, self.r1.id)

        logic.update_waymarks()

        self.assertEqual(models.Waymark.objects.all().count(), 9)
        waymark = storage.waymarks.look_for_road(point_from=self.p1.id, point_to=self.p3.id)
        self.assertEqual(waymark.road.id, r3.id)

        self.assertNotEqual(r3.id, self.r1.id)

    def test_roll_road(self):
        self.assertEqual(prototypes.RoadPrototype._roll(5, 4, 13, 8), 'rdrrdrrdrrdr')
        self.assertEqual(prototypes.RoadPrototype._roll(13, 8, 5, 4), 'llullullullu')
        self.assertEqual(prototypes.RoadPrototype._roll(5, 8, 13, 4), 'rrurrurrurru')
        self.assertEqual(prototypes.RoadPrototype._roll(13, 4, 5, 8), 'ldlldlldlldl')

        self.assertEqual(prototypes.RoadPrototype._roll(0, 4, 0, 8), 'dddd')
        self.assertEqual(prototypes.RoadPrototype._roll(0, 8, 0, 4), 'uuuu')
        self.assertEqual(prototypes.RoadPrototype._roll(5, 0, 13, 0), 'rrrrrrrr')
        self.assertEqual(prototypes.RoadPrototype._roll(13, 0, 5, 0), 'llllllll')

        self.assertEqual(prototypes.RoadPrototype._roll(5, 12, 3, 17), 'dlddldd')
