

def sum_series(generator, n):
    return sum(generator(i) for i in range(n))


def series(generator, n):
    return [generator(i) for i in range(n)]


def search_bordered_sum_series(generator_fabric, n, left_x, right_x, border, epsilon=0.01**5):
    left_y = sum_series(generator_fabric(left_x), n)
    right_y = sum_series(generator_fabric(right_x), n)

    if not (left_y < border < right_y):
        raise NotImplementedError

    while True:

        if right_y - left_y < epsilon:
            break

        if right_x - left_x < epsilon:
            break

        new_x = (left_x + right_x) / 2
        new_y = sum_series(generator_fabric(new_x), n)

        if new_y < border:
            left_x = new_x
            left_y = new_y
            continue

        if border < new_y:
            right_x = new_x
            right_y = new_y
            continue

        raise NotImplementedError

    return series(generator_fabric(left_x), n)


class ExponentialSeriesGenerator:
    __slots__ = ('base', 'left_x', 'right_x')

    def __init__(self, base, left_x=0, right_x=2**8):
        self.base = base
        self.left_x = left_x
        self.right_x = right_x

    def generator_fabric(self, k):
        def generator(i):
            return self.base * k ** i

        return generator

    def series(self, n, border):
        return search_bordered_sum_series(generator_fabric=self.generator_fabric,
                                          n=n,
                                          left_x=self.left_x,
                                          right_x=self.right_x,
                                          border=border)


def time_series_to_values(time_series, start_speed, end_speed, rounder):
    total_time = sum(time_series)

    speed_delta = (end_speed - start_speed) / total_time

    values = []

    prev_time = 0
    prev_experience = 0

    for time in time_series:
        next_time = prev_time + time
        next_experience = next_time * (start_speed + (start_speed + next_time * speed_delta)) / 2

        values.append(next_experience - prev_experience)

        prev_time = next_time
        prev_experience = next_experience

    return [rounder(value) for value in values]
