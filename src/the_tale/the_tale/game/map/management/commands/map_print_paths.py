import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'print text map with found paths for every risk level'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):

        paths = []

        modifiers = {place.id: 1 for place in places_storage.places.all()}

        for risk in heroes_relations.RISK_LEVEL.records:
            paths.append(storage.cells.find_path_to_place(from_x=37, from_y=8, to_place_id=28, cost_modifiers=modifiers, risk_level=risk))

        m = [['.' for i in range(conf.settings.WIDTH)] for j in range(conf.settings.HEIGHT)]

        for road in roads_storage.roads.all():
            for x, y in road.get_cells():
                m[y][x] = 'r'

        for i, path in enumerate(paths):
            for x, y in path._cells:
                m[y][x] = str(i+1)

        for place in places_storage.places.all():
            m[place.y][place.x] = '#'

        self.logger.info('\n'.join(''.join(row) for row in m))
