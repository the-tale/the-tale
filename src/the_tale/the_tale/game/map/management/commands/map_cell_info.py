
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'generate map'

    LOCKS = ['game_commands']

    requires_model_validation = False

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-x', action='store', type=int, dest='x', required=True, help='x coordinate')
        parser.add_argument('-y', action='store', type=int, dest='y', required=True, help='y coordinate')

    def _handle(self, *args, **options):

        x = options['x']
        y = options['y']

        world_generator = prototypes.WorldInfoPrototype.get_by_id(storage.map_info.item.world_id).generator

        cell = world_generator.cell_info(x, y)
        power_cell = world_generator.cell_power_info(x, y)

        self.logger.info('----CELL--x=%d--y=%d--' % (x, y))
        self.logger.info('height:            %.2f \t\t| %r       ' % (cell.height, power_cell.height))
        self.logger.info('temperature:       %.2f \t\t| %f       ' % (cell.temperature, power_cell.temperature))
        self.logger.info('wind:              (%.2f, %.2f) \t| %r ' % (cell.wind[0], cell.wind[1], power_cell.wind))
        self.logger.info('wetness:           %.2f \t\t| %f       ' % (cell.wetness, power_cell.wetness))
        self.logger.info('vegetation:        %.2f \t\t| %r       ' % (cell.vegetation, power_cell.vegetation))
        self.logger.info('soil:              %.2f \t\t| %f       ' % (cell.soil, power_cell.soil))
        self.logger.info('atmo_wind:         (%.2f, %.2f) \t|    ' % cell.atmo_wind)
        self.logger.info('atmo_temperature:  %.2f \t\t|          ' % (cell.atmo_temperature,))
        self.logger.info('atmo_wetness:      %.2f \t\t|          ' % (cell.atmo_wetness,))

        terrain_points = []
        for terrain in relations.TERRAIN.records:
            biom = generator.biomes.Biom(id_=terrain)
            terrain_points.append((terrain.text, biom.check(cell), biom.get_points(cell)))
        terrain_points = sorted(terrain_points, key=lambda x: -x[1])

        self.logger.info('')
        self.logger.info('----TERRAIN----')
        for biom_name, total_power, aspects in terrain_points[:5]:
            self.logger.info('%.2f\t%s' % (total_power, biom_name))

            for aspect_name, aspect_value in aspects:
                self.logger.info('\t%.2f\t%s' % (aspect_value, aspect_name))

        self.logger.info('')
        self.logger.info('----POINTS----')

        points = []
        for point in generator.power_points.get_power_points():
            value = point.log_powers_for(world_generator, x=x, y=y)
            if value:
                points.append((point.name, value))
        points.sort()

        for name, value in points:
            self.logger.info('%s %r' % (name.ljust(35), value))
