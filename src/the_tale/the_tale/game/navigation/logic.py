
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
