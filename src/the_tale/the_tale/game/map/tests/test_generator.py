
import smart_imports

smart_imports.all()


class GeneratorTests(utils_testcase.TestCase):

    def setUp(self):
        super(GeneratorTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_ui_cell_serialization(self):
        world_info = prototypes.WorldInfoPrototype.get_by_id(storage.map_info.item.world_id).generator

        world_cell = world_info.cell_info(random.randint(0, world_info.w - 1), random.randint(0, world_info.h - 1))

        ui_cell = generator.descriptors.UICell(world_cell)

        self.assertEqual(ui_cell.serialize(), generator.descriptors.UICell.deserialize(ui_cell.serialize()).serialize())

    def test_ui_cells_serialization(self):
        world_info = prototypes.WorldInfoPrototype.get_by_id(storage.map_info.item.world_id).generator

        cells = generator.descriptors.UICells(world_info)

        self.assertEqual(cells.serialize(), generator.descriptors.UICells.deserialize(cells.serialize()).serialize())


def create_test_building_power_point(building_type):

    def test_building_power_point(self):
        building = places_logic.create_building(self.place_1.persons[0], utg_name=game_names.generator().get_test_name('building-name'))

        self.assertTrue(len(generator.power_points.get_building_power_points(building)) > 0)

    return test_building_power_point


for record in places_relations.BUILDING_TYPE.records:
    method = create_test_building_power_point(record)
    setattr(GeneratorTests, 'test_%s' % record.name, method)
