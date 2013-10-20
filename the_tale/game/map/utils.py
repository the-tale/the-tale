# coding: utf-8

from game.relations import RACE

def get_race_percents(persons):

    race_powers = dict( (race.value, 0) for race in RACE._records)
    for person in persons:
        race_powers[person.race.value] += person.power

    total_power = sum(race_powers.values()) + 1 # +1 - to prevent division by 0

    return dict( (race_id, float(power) / total_power) for race_id, power in race_powers.items())
