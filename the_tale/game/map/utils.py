# coding: utf-8

from the_tale.game.relations import RACE

def get_person_race_percents(persons):
    race_powers = dict( (race.value, 0) for race in RACE.records)

    powers = [person.politic_power for person in persons]

    for person in persons:
        race_powers[person.race.value] += person.politic_power.total_politic_power_fraction(powers)

    return race_powers


def get_race_percents(places):
    race_powers = dict( (race.value, 0) for race in RACE.records)

    for place in places:
        for race in RACE.records:
            race_powers[race.value] += place.races.get_race_percents(race) * place.attrs.size

    total_power = sum(race_powers.values()) + 1 # +1 - to prevent division by 0

    return dict( (race_id, float(power) / total_power) for race_id, power in race_powers.items())
