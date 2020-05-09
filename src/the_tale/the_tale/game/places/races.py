
import smart_imports

smart_imports.all()


E = 0.001


class RaceInfo(typing.NamedTuple):
    race: rels.relations.Record
    percents: float
    optimal_percents: float
    persons_percents: float
    delta: float


class Races(object):

    def __init__(self, races=None):
        if races is None:
            races = {race: 1.0 / len(game_relations.RACE.records) for race in game_relations.RACE.records}

        self._races = races

    def serialize(self):
        return {race.value: percents for race, percents in self._races.items()}

    @classmethod
    def deserialize(cls, data):
        return cls(races={game_relations.RACE(int(race_id)): percents for race_id, percents in data.items()})

    def get_race_percents(self, race):
        return self._races.get(race, 0)

    def get_optimal_pressure(self, persons, demographics_pressure_modifires):
        trends = {race: 0.0 for race in game_relations.RACE.records}

        for person in persons:
            pressure = person.attrs.demographics_pressure + demographics_pressure_modifires.get(person.race, 0)
            delta = politic_power_storage.persons.total_power_fraction(person.id) * pressure
            trends[person.race] += delta

        # normalize trends
        normalizer = sum(trends.values())

        if not trends or normalizer < E:
            return copy.copy(self._races)

        return {race: float(power) / normalizer for race, power in trends.items()}

    def get_next_races(self, persons, demographics_pressure_modifires):
        trends = self.get_optimal_pressure(persons, demographics_pressure_modifires)

        new_races = {race: max(0.0, percents + c.PLACE_RACE_CHANGE_DELTA * trends[race]) for race, percents in self._races.items()}

        # normalize
        normalizer = sum(new_races.values())

        new_races = {race: percents / normalizer for race, percents in new_races.items()}

        return new_races

    def update(self, persons, demographics_pressure_modifires):
        self._races = self.get_next_races(persons, demographics_pressure_modifires)

    @property
    def dominant_race(self):
        if self._races:
            return max(self._races.items(), key=lambda x: x[1])[0]
        return None

    def get_next_delta(self, persons, demographics_pressure_modifires):
        next_races = self.get_next_races(persons, demographics_pressure_modifires)

        return {race: next_races[race] - self._races[race] for race in game_relations.RACE.records}

    def demographics(self, persons, demographics_pressure_modifires):
        races = []

        trends = self.get_optimal_pressure(persons, demographics_pressure_modifires)

        next_delta = self.get_next_delta(persons, demographics_pressure_modifires)

        persons_percents = map_logic.get_person_race_percents(persons)

        for race in game_relations.RACE.records:
            races.append(RaceInfo(race=race,
                                  percents=self._races[race],
                                  optimal_percents=trends[race],
                                  delta=next_delta[race],
                                  persons_percents=persons_percents[race.value]))

        return sorted(races, key=lambda r: -r.percents)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self._races == other.races)

    def __ne__(self, other):
        return not self.__eq__(other)
