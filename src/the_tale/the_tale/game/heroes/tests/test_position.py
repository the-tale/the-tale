
import smart_imports

smart_imports.all()


class HeroPositionTest(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account.id)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.road_1_2 = roads_logic.road_between_places(self.place_1, self.place_2)
        self.road_2_3 = roads_logic.road_between_places(self.place_2, self.place_3)

    def test_initialize(self):
        self.assertNotEqual(self.hero.position.place_id, None)

        self.assertEqual(self.hero.position.x, self.hero.position.place.x)
        self.assertEqual(self.hero.position.y, self.hero.position.place.y)
        self.assertEqual(self.hero.position.dx, 0)
        self.assertEqual(self.hero.position.dy, 0)

        self.assertFalse(self.hero.position.moved_out_place)

    def test_set_position(self):
        old_position = copy.deepcopy(self.hero.position)

        self.hero.position.set_position(x=self.hero.position.x + 0.2,
                                        y=self.hero.position.y - 0.7)

        self.assertEqual(self.hero.position.place_id, None)
        self.assertEqual(self.hero.position.x, old_position.x + 0.2)
        self.assertEqual(self.hero.position.y, old_position.y - 0.7)
        self.assertEqual(self.hero.position.cell_x, old_position.cell_x)
        self.assertEqual(self.hero.position.cell_y, old_position.cell_y - 1)

        self.hero.position.set_position(x=self.hero.position.x + 0.2,
                                        y=self.hero.position.y - 0.7)

        self.assertEqual(self.hero.position.place_id, None)

    def test_can_visit_current_place__in_place(self):
        pos = position.Position.create(place=self.place_1)
        pos.set_position(x=pos.x + 0.4, y=pos.y - 0.2)

        self.assertFalse(pos.can_visit_current_place(delta=0.1))
        self.assertFalse(pos.can_visit_current_place(delta=0.3))
        self.assertTrue(pos.can_visit_current_place(delta=0.45))

    def test_can_visit_current_place__out_place(self):
        pos = position.Position.create(place=self.place_1)
        pos.set_position(x=pos.x + 1.4, y=pos.y - 0.2)

        self.assertFalse(pos.can_visit_current_place(delta=0.1))
        self.assertFalse(pos.can_visit_current_place(delta=0.3))
        self.assertFalse(pos.can_visit_current_place(delta=0.45))
