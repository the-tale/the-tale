# coding: utf-8

import copy
import collections

from the_tale.game.relations import RACE

from the_tale.game.balance import constants as c
from the_tale.game.map.utils import get_race_percents

E = 0.001


class RaceInfo(collections.namedtuple('RaceInfo', ['race', 'percents', 'persons_percents', 'delta'])):
    pass

class Races(object):

    def __init__(self, data):
        self._data = data

        if not self._data:
            self._data.update({race.value: 1.0 / len(RACE.records) for race in RACE.records})

        self._races = {RACE(int(race_id)):percents for race_id, percents in self._data.iteritems()}


    def serialize(self):
        self._data.clear()
        self._data.update({race.value: percents for race, percents in self._races.iteritems()})

    def get_race_percents(self, race):
        return self._races.get(race, 0)


    def get_next_races(self, persons):
        trends = {race: 0.0 for race in RACE.records}

        for person in persons:
            trends[person.race] += person.power

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

        persons_percents = get_race_percents(persons)

        for race in RACE.records:
            races.append(RaceInfo(race=race, percents=self._races[race], delta=next_delta[race], persons_percents=persons_percents[race.value]))

        return sorted(races, key=lambda r: -r.percents)
