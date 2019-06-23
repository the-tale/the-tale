
import smart_imports

smart_imports.all()


MAX_COST = 999999999999999999999


def euclidean_distance(x_1, y_1, x_2, y_2):
    return math.hypot(x_1 - x_2, y_1 - y_2)


def manhattan_distance(x_1, y_1, x_2, y_2):
    return abs(x_1 - x_2) + abs(y_1 - y_2)


def normalise_path(path):
    cells = set(path)

    if len(cells) == len(path):
        return path

    reversed_path = path.copy()
    reversed_path.reverse()

    new_path = []

    n = len(path)

    i = 0

    while i < n:
        i = n - 1 - reversed_path.index(path[i])

        new_path.append(path[i])

        i += 1

    return new_path


def nearest_point_on_section(x_0, y_0, x_1, y_1, x_2, y_2):

    if (x_1, y_1) == (x_2, y_2):
        return euclidean_distance(x_0, y_0, x_1, y_1), 0.0, x_1, y_1

    distance = abs((y_2 - y_1) * x_0 - (x_2 - x_1) * y_0 + x_2 * y_1 - y_2 * x_1) / euclidean_distance(x_1, y_1, x_2, y_2)

    hypot_a = euclidean_distance(x_0, y_0, x_1, y_1)
    hypot_b = euclidean_distance(x_0, y_0, x_2, y_2)
    hypot_c = euclidean_distance(x_1, y_1, x_2, y_2)

    cathetus_a = math.sqrt(hypot_a**2 - distance**2) if hypot_a >= distance else 0
    cathetus_b = math.sqrt(hypot_b**2 - distance**2) if hypot_b >= distance else 0

    # умножаем на 3, так как у нас может быть 3 значения с ошибками округления (hypot_c, cathetus_a, cathetus_b)
    if hypot_c + sys.float_info.epsilon * 3 < cathetus_a + cathetus_b:

        if cathetus_a < cathetus_b:
            return hypot_a, 0.0, x_1, y_1

        else:
            return hypot_b, 1.0, x_2, y_2

    percents = max(0.0, min(1.0, cathetus_a / hypot_c))

    x = x_1 + (x_2 - x_1) * percents
    y = y_1 + (y_2 - y_1) * percents

    return distance, percents, x, y
