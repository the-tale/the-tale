# -*- coding: utf-8 -*-

from .roads import PATH_DIRECTION

def square_length(x0, y0, x1, y1):
    return (x0-x1)**2 + (y0-y1)**2

def roll_road(road, start_x, start_y, finish_x, finish_y):
    x = start_x
    y = start_y

    while x != finish_x or y != finish_y:
        directions = [ (PATH_DIRECTION.LEFT, square_length(x-1, y, finish_x, finish_y), x-1, y ), 
                       (PATH_DIRECTION.RIGHT, square_length(x+1, y, finish_x, finish_y), x+1, y ),
                       (PATH_DIRECTION.UP, square_length(x, y-1, finish_x, finish_y), x, y-1 ),
                       (PATH_DIRECTION.DOWN, square_length(x, y+1, finish_x, finish_y), x, y+1 ) ]

        direction, length, x, y = min(directions, key=lambda x: x[1])

        road.add_path_direction(direction)
