# coding: utf-8

import copy
import collections

from the_tale.game.relations import RACE

from the_tale.game.balance import constants as c
from the_tale.game.map.utils import get_person_race_percents

E = 0.001


class RaceInfo(collections.namedtuple('RaceInfo', ['race', 'percents', 'persons_percents', 'delta'])):
    pass


class Races(object):

    def __init__(self, races=None):
        if races is None:
            races = {race: 1.0 / len(RACE.records) for race in RACE.records}

        self._races = races


    def serialize(self):
        return {race.value: percents for race, percents in self._races.iteritems()}

    @classmethod
    def deserialize(cls, data):
        return cls(races={ RACE(int(race_id)): percents for race_id, percents in data.iteritems() })

    def get_race_percents(self, race):
        return self._races.get(race, 0)


    def get_next_races(self, persons):
        trends = {race: 0.0 for race in RACE.records}

        for person in persons:
            trends[person.race] += person.total_politic_power_fraction * person.attrs.demographics_pressure

        # normalize trends
        normalizer = sum(trends.values())

        if not trends or normalizer < E:
            return copy.copy(self._races)

        trends = {race: float(power) / normalizer for race, power in trends.iteritems()}

        new_races = {race: max(0.0, percents + c.PLACE_RACE_CHANGE_DELTA * trends[race]) for race, percents in self._races.iteritems()}

        # normalize
        normalizer = sum(new_races.itervalues())

        new_races = {race: percents/normalizer for race, percents in new_races.iteritems()}

        return new_races


    def update(self, persons):
        self._races = self.get_next_races(persons)


    @property
    def dominant_race(self):
        if self._races:
            return max(self._races.items(), key=lambda x: x[1])[0]
        return None


    def get_next_delta(self, persons):
        next_races = self.get_next_races(persons)

        return {race: next_races[race] - self._races[race] for race in RACE.records}


    def demographics(self, persons):
        races = []

        next_delta = self.get_next_delta(persons)

        persons_percents = get_person_race_percents(persons)

        for race in RACE.records:
            races.append(RaceInfo(race=race, percents=self._races[race], delta=next_delta[race], persons_percents=persons_percents[race.value]))

        return sorted(races, key=lambda r: -r.percents)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self._races == other.races)

    def __ne__(self, other):
        return not self.__eq__(other)
