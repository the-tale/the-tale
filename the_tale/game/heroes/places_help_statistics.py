# coding: utf-8

import collections

from the_tale.game.places import storage as places_storage

from the_tale.game.heroes.conf import heroes_settings


class PlacesHelpStatistics(object):

    __slots__ = ('history', 'updated')

    def __init__(self):
        self.history = collections.deque(maxlen=heroes_settings.PLACE_HELP_HISTORY_SIZE)
        self.updated = False

    def serialize(self):
        return {'history': list(self.history)}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.history = collections.deque(data.get('history', []), maxlen=heroes_settings.PLACE_HELP_HISTORY_SIZE)
        return obj

    def add_place(self, place_id, value=1):
        self.updated = True
        self.history.append((place_id, value))

    def _get_places_statisitcs(self):
        counter = collections.Counter()
        for place_id, value in self.history:
            counter.update({place_id: value})
        return counter

    def _get_most_common_places(self):
        return self._get_places_statisitcs().most_common()

    def get_most_common_places(self):
        return [ (places_storage.places[place_id], number) for place_id, number in  self._get_most_common_places()]

    def get_allowed_places_ids(self, number):

        common_places = self._get_most_common_places()

        number -= 1

        if number >= len(common_places):
            number = len(common_places) - 1

        if number < 0:
            return []

        min_helps_number = common_places[number][1]
        return [place_id for place_id, helps_number in common_places if helps_number >= min_helps_number]

    def _reset(self):
        self.updated = True
        self.history = collections.deque(maxlen=heroes_settings.PLACE_HELP_HISTORY_SIZE)
