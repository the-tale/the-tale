
import smart_imports

smart_imports.all()


class PowerStorage:
    __slots__ = ('turn',

                 '_inner_power',
                 '_outer_power',

                 '_inner_power_fraction',
                 '_outer_power_fraction')

    TARGET_TYPE = NotImplemented

    def __init__(self):
        self.reset()

    def reset(self):
        self.turn = None

        self._inner_power = None
        self._outer_power = None

        self._inner_power_fraction = None
        self._outer_power_fraction = None

    @staticmethod
    def _fill_powers(powers, impacts):
        for impact in impacts:
            powers[impact.target_id] = impact.amount

    def _tt_targets_ids(self):
        raise NotImplementedError

    def _update_fractions(self):
        raise NotImplementedError

    def sync(self):
        if self.turn == game_turn.number():
            return

        self.turn = game_turn.number()

        targets_ids = self._tt_targets_ids()

        self._inner_power = {target_id: 0 for target_id in targets_ids}
        self._outer_power = {target_id: 0 for target_id in targets_ids}

        targets = [(self.TARGET_TYPE, target_id) for target_id in targets_ids]

        impacts = game_tt_services.personal_impacts.cmd_get_targets_impacts(targets=targets)

        self._fill_powers(self._inner_power, impacts)

        impacts = game_tt_services.crowd_impacts.cmd_get_targets_impacts(targets=targets)

        self._fill_powers(self._outer_power, impacts)

        self._update_fractions()

    def total_power_fraction(self, target_id):
        self.sync()
        return (self._inner_power_fraction[target_id] + self._outer_power_fraction[target_id]) / 2

    def inner_power_fraction(self, target_id):
        self.sync()
        return self._inner_power_fraction[target_id]

    def inner_power(self, target_id):
        self.sync()
        return self._inner_power[target_id]

    def outer_power_fraction(self, target_id):
        self.sync()
        return self._outer_power_fraction[target_id]

    def outer_power(self, target_id):
        self.sync()
        return self._outer_power[target_id]

    def ui_info(self, target_id):
        self.sync()
        return {'inner': {'value': self.inner_power(target_id),
                          'fraction': self.inner_power_fraction(target_id)},
                'outer': {'value': self.outer_power(target_id),
                          'fraction': self.outer_power_fraction(target_id)},
                'fraction': self.total_power_fraction(target_id)}


class PlacesPowerStorage(PowerStorage):
    TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.PLACE

    def _tt_targets_ids(self):
        return [place.id for place in places_storage.places.all()]

    def _update_fractions(self):
        self._inner_power_fraction = {}
        self._outer_power_fraction = {}

        self._inner_power_fraction.update(logic.calculate_power_fractions({place_id: power
                                                                           for place_id, power in self._inner_power.items()
                                                                           if places_storage.places[place_id].is_frontier}))
        self._inner_power_fraction.update(logic.calculate_power_fractions({place_id: power
                                                                           for place_id, power in self._inner_power.items()
                                                                           if not places_storage.places[place_id].is_frontier}))

        self._outer_power_fraction.update(logic.calculate_power_fractions({place_id: power
                                                                           for place_id, power in self._outer_power.items()
                                                                           if places_storage.places[place_id].is_frontier}))
        self._outer_power_fraction.update(logic.calculate_power_fractions({place_id: power
                                                                           for place_id, power in self._outer_power.items()
                                                                           if not places_storage.places[place_id].is_frontier}))


class PersonsPowerStorage(PowerStorage):
    TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.PERSON

    def _tt_targets_ids(self):
        return [person.id for person in persons_storage.persons.all()]

    def _update_fractions(self):
        self._inner_power_fraction = {}
        self._outer_power_fraction = {}

        for place in places_storage.places.all():
            self._inner_power_fraction.update(logic.calculate_power_fractions({person.id: self._inner_power[person.id]
                                                                               for person in place.persons}))
            self._outer_power_fraction.update(logic.calculate_power_fractions({person.id: self._outer_power[person.id]
                                                                               for person in place.persons}))


places = PlacesPowerStorage()
persons = PersonsPowerStorage()
