
import smart_imports

smart_imports.all()


MAX_COST = 999999999999999999999


def euclidean_distance(x_1, y_1, x_2, y_2):
    return math.hypot(x_1 - x_2, y_1 - y_2)


def manhattan_distance(x_1, y_1, x_2, y_2):
    return abs(x_1 - x_2) + abs(y_1 - y_2)
