# -*- coding: utf-8 -*-
import random
import postmarkup

from dext.utils import s11n

from game.game_info import GENDER
from textgen import words

from common.utils.prototypes import BasePrototype

from game import names
from game.prototypes import TimePrototype, GameTime

from game.balance import formulas as f
from game.balance.enums import RACE, PERSON_TYPE

from game.helpers import add_power_management

from game.heroes.models import Hero

from game.map.places.models import Place
from game.map.places.conf import places_settings
from game.map.places.exceptions import PlacesException
from game.map.places.modifiers import MODIFIERS, PlaceModifierBase
from game.map.places import signals

@add_power_management(places_settings.POWER_HISTORY_LENGTH, PlacesException)
class PlacePrototype(BasePrototype):
    _model_class = Place
    _readonly = ('id', 'x', 'y', 'name', 'type', 'heroes_number')
    _bidirectional = ('description', 'size')
    _get_by = ('id',)

    @classmethod
    def get_by_coordinates(cls, x, y):
        try:
            return cls(Place.objects.get(x=x, y=y))
        except Place.DoesNotExist:
            return None

    @property
    def updated_at_game_time(self): return GameTime(*f.turns_to_game_time(self._model.updated_at_turn))

    def get_modifier(self): return MODIFIERS[self._model.modifier](self) if self._model.modifier is not None else None
    def set_modifier(self, value):
        if isinstance(value, PlaceModifierBase):
            self._model.modifier = value.get_id()
        else:
            self._model.modifier = value
    modifier = property(get_modifier, set_modifier)

    def sync_modifier(self):
        if self.modifier and not self.modifier.is_enough_power:
            old_modifier = self.modifier
            self.modifier = None
            signals.place_modifier_reseted.send(self.__class__, place=self, old_modifier=old_modifier)

    @property
    def normalized_name(self):
        if not hasattr(self, '_normalized_name'):
            self._normalized_name = words.WordBase.deserialize(s11n.from_json(self._model.name_forms))
        return self._normalized_name
        # return (self._normalized_name, u'загл')

    def set_name_forms(self, name_forms):
        self._model.name_forms = s11n.to_json(name_forms.serialize())
        self._normalized_name = name_forms
        self._model.name = name_forms.normalized

    @property
    def description_html(self): return postmarkup.render_bbcode(self._model.description)

    @property
    def terrain_change_power(self):
        power = self.size
        if self.modifier:
            power = self.modifier.modify_terrain_change_power(power)
        return int(round(power))

    def update_heroes_number(self):
        current_turn = TimePrototype.get_current_turn_number()
        self._model.heroes_number = Hero.objects.filter(pref_place_id=self.id, active_state_end_at__gte=current_turn).count()

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

    def mark_as_updated(self): self._model.updated_at_turn = TimePrototype.get_current_turn_number()

    @property
    def max_persons_number(self): return places_settings.SIZE_TO_PERSONS_NUMBER[self.size]

    def sync_persons(self):
        '''
        DO NOT SAVE CHANGES - this MUST do parent code
        '''
        from game.persons.prototypes import PersonPrototype
        from game.persons.storage import persons_storage

        for person in filter(lambda person: not person.is_stable, self.persons):
            person.move_out_game()
            signals.place_person_left.send(self.__class__, place=self, person=person)

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
            signals.place_person_arrived.send(self.__class__, place=self, person=new_person)

        self.sync_race()

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self._model.data)
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


    def get_race(self):
        if not hasattr(self, '_race'):
            self._race = RACE(self._model.race)
        return self._race
    def set_race(self, value):
        self.race.update(value)
        self._model.race = self.race.value
    race = property(get_race, set_race)

    def sync_race(self):
        race_power = {}

        for person in self.persons:
            race_power[person.race] = race_power.get(person.race, 0) + person.power

        if len(race_power) == 0:
            return

        dominant_race = max(race_power.items(), key=lambda x: x[1])[0]

        if self.race != dominant_race:
            old_race = self.race
            self.race = dominant_race
            signals.place_race_changed.send(self.__class__, place=self, old_race=old_race, new_race=self.race)


    ###########################################
    # Object operations
    ###########################################

    def remove(self): self._model.delete()
    def save(self):
        self._model.data = s11n.to_json(self.data)
        self._model.save(force_update=True)

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'race': self.race.value,
                'name': self.name,
                'type': self.type,
                'size': self.size}
