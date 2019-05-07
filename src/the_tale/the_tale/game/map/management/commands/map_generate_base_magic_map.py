
import smart_imports

smart_imports.all()


W = map_conf.settings.WIDTH
H = map_conf.settings.HEIGHT

MAGIC_STEP = 0.4

BASE_PLACE_MAGIC = 0.2
BASE_ROAD_MAGIC = BASE_PLACE_MAGIC + MAGIC_STEP

MAX_MAGIC = 3.0

RANDOM_FRACTION = 0.33


def get_cells(i, j):

    cells = []

    for d_1 in (-1, 0, 1):
        for d_2 in (-1, 0, 1):
            if d_1 == d_2 == 0:
                continue

            if not (0 <= i + d_1 < H):
                continue

            if not (0 <= j + d_2 < W):
                continue

            cells.append((j+d_2, i+d_1))

    return cells


def fill_cell_magic(m, i, j):

    if m[i][j] != 0:
        return False

    cells = get_cells(i, j)

    magics = []

    for x, y in cells:
        if m[y][x] == 0:
            continue

        magics.append(m[y][x] + MAGIC_STEP)

    if not magics:
        return False

    m[i][j] = min(min(magics), MAX_MAGIC)

    return True


class Command(django_management.BaseCommand):

    help = 'Generate base magic map'

    def handle(self, *args, **options):

        m = []

        for i in range(0, H):
            m.append([0 for j in range(0, W)])

        for place in places_storage.places.all():
            m[place.y][place.x] = BASE_PLACE_MAGIC

        for road in roads_storage.roads.all():
            for x, y in road.get_cells():
                if m[y][x] != 0:
                    continue

                m[y][x] = BASE_ROAD_MAGIC

        changed = True

        while changed:

            changed = False

            for i in range(H):
                for j in range(W):
                    changed = changed or fill_cell_magic(m, i, j)

        for i in range(H):
            for j in range(W):
                x = m[i][j]
                m[i][j] = random.uniform((x * (1 - RANDOM_FRACTION)),
                                         (x * (1 + RANDOM_FRACTION)))

        print(json.dumps({'width': W,
                          'height': H,
                          'magic': m}))
