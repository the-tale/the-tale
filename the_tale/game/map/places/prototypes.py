# -*- coding: utf-8 -*-
import random
import postmarkup

from dext.utils import s11n

from game.game_info import GENDER
from textgen import words

from game import names
from game.prototypes import TimePrototype, GameTime
from game.balance import formulas as f
from game.helpers import add_power_management

from game.heroes.models import Hero

from game.map.places.models import Place, PLACE_TYPE
from game.map.places.conf import places_settings
from game.map.places.exceptions import PlacesException
from game.map.places.modifiers import MODIFIERS, PlaceModifierBase

@add_power_management(places_settings.POWER_HISTORY_LENGTH, PlacesException)
class PlacePrototype(object):

    TYPE = 'BASE'

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Place.objects.get(id=id_))
        except Place.DoesNotExist:
            return None

    @classmethod
    def get_by_coordinates(cls, x, y):
        try:
            return cls(Place.objects.get(x=x, y=y))
        except Place.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def x(self): return self.model.x

    @property
    def y(self): return self.model.y

    def get_name(self): return self.model.name
    def set_name(self, value): self.model.name = value
    name = property(get_name, set_name)

    @property
    def updated_at_game_time(self): return GameTime(*f.turns_to_game_time(self.model.updated_at_turn))

    def get_modifier(self): return MODIFIERS[self.model.modifier](self) if self.model.modifier is not None else None
    def set_modifier(self, value):
        if isinstance(value, PlaceModifierBase):
            self.model.modifier = value.get_id()
        else:
            self.model.modifier = value
    modifier = property(get_modifier, set_modifier)

    @property
    def normalized_name(self):

        if not hasattr(self, '_normalized_name'):
            self._normalized_name = words.WordBase.deserialize(s11n.from_json(self.model.name_forms))

        return (self._normalized_name, u'загл')

    def set_name_forms(self, name_forms):
        self.model.name_forms = s11n.to_json(name_forms.serialize())
        if hasattr(self, '_normalized_name'):
            delattr(self, '_normalized_name')

    def get_descriotion(self): return self.model.description
    def set_description(self, value): self.model.description = value
    description = property(get_descriotion, set_description)

    @property
    def description_html(self): return postmarkup.render_bbcode(self.model.description)

    @property
    def type(self): return self.model.type

    def get_size(self): return self.model.size
    def set_size(self, value): self.model.size = value
    size = property(get_size, set_size)

    @property
    def terrain_change_power(self):
        power = self.size
        if self.modifier:
            power = self.modifier.modify_terrain_change_power(power)
        return int(round(power))

    @property
    def heroes_number(self): return self.model.heroes_number
    def update_heroes_number(self):
        current_turn = TimePrototype.get_current_turn_number()
        self.model.heroes_number = Hero.objects.filter(pref_place_id=self.id, active_state_end_at__gte=current_turn).count()

    @property
    def persons(self):
        from game.persons.storage import persons_storage
        from game.persons.models import PERSON_STATE
        return sorted(persons_storage.filter(place_id=self.id, state=PERSON_STATE.IN_GAME), key=lambda p: -p.power)

    @property
    def total_persons_power(self): return sum([person.power for person in self.persons])

    @property
    def modifiers(self):
        from game.map.places.modifiers import MODIFIERS
        return sorted([modifier(self) for modifier in MODIFIERS.values()], key=lambda m: -m.power)

    def mark_as_updated(self): self.model.updated_at_turn = TimePrototype.get_current_turn_number()

    @property
    def max_persons_number(self): return places_settings.SIZE_TO_PERSONS_NUMBER[self.size]

    def sync_persons(self):
        '''
        DO NOT SAVE CHANGES - this MUST do parent code
        '''
        from game.persons.prototypes import PersonPrototype
        from game.persons.storage import persons_storage
        from game.balance.enums import RACE, PERSON_TYPE

        for person in filter(lambda person: not person.is_stable, self.persons):
            person.move_out_game()

        persons_count = len(self.persons)

        while persons_count < self.max_persons_number:
            race = random.choice(RACE._ALL)
            gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

            new_person = PersonPrototype.create(place=self,
                                                race=race,
                                                gender=gender,
                                                tp=random.choice(PERSON_TYPE._ALL),
                                                name=names.generator.get_name(race, gender))
            persons_storage.add_item(new_person.id, new_person)
            persons_count += 1

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
            if 'nearest_cells' in self._data:
                self._data['nearest_cells'] = map(tuple, self._data['nearest_cells'])
        return self._data

    def get_nearest_cells(self):
        if 'nearest_cells' not in self.data:
            self.data['nearest_cells'] = []
        return self.data['nearest_cells']
    def set_nearest_cells(self, value): self.data['nearest_cells'] = value
    nearest_cells = property(get_nearest_cells, set_nearest_cells)

    @property
    def terrains(self):
        from game.map.storage import map_info_storage
        map_info = map_info_storage.item
        terrains = set()
        for cell in self.nearest_cells:
            terrains.add(map_info.terrain[cell[1]][cell[0]])
        return terrains

    def get_dominant_race(self):
        race_power = {}

        for person in self.persons:
            race_power[person.race] = race_power.get(person.race, 0) + person.power

        if len(race_power) == 0:
            return

        dominant_race = max(race_power.items(), key=lambda x: x[1])[0]

        return dominant_race

    def __unicode__(self):
        return self.model.__unicode__()

    def __repr__(self):
        return self.model.__repr__()

    ###########################################
    # Checks
    ###########################################

    @property
    def is_settlement(self): return self.type in [PLACE_TYPE.CITY]

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self):
        self.model.data = s11n.to_json(self.data)
        self.model.save(force_update=True)

    # def __eq__(self, other):
    #     return self.id == other.id

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'name': self.name,
                'type': self.type,
                'size': self.size}
