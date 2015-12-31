# coding: utf-8
import random
import datetime

from the_tale import amqp_environment

from the_tale.common.utils import bbcode

from the_tale.game import names

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.prototypes import TimePrototype, GameTime

from . import conf
from . import modifiers
from . import signals
from . import effects
from . import relations


class Place(names.ManageNameMixin2):
    __slots__ = ('id',
                 'x', 'y',
                 'heroes_number',
                 'updated_at',
                 'updated_at_turn',
                 'created_at',
                 'created_at_turn',
                 'habit_honor',
                 'habit_honor_positive',
                 'habit_honor_negative',
                 'habit_peacefulness',
                 'habit_peacefulness_positive',
                 'habit_peacefulness_negative',
                 'is_frontier',
                 'description',
                 'race',
                 'persons_changed_at_turn',
                 'power',
                 'attrs',
                 'utg_name',
                 'races',
                 'nearest_cells',
                 'effects',
                 'modifier',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 x, y,
                 heroes_number,
                 updated_at,
                 updated_at_turn,
                 created_at,
                 created_at_turn,
                 habit_honor,
                 habit_honor_positive,
                 habit_honor_negative,
                 habit_peacefulness,
                 habit_peacefulness_positive,
                 habit_peacefulness_negative,
                 is_frontier,
                 description,
                 race,
                 persons_changed_at_turn,
                 power,
                 attrs,
                 utg_name,
                 races,
                 nearest_cells,
                 effects,
                 modifier):
        self.id = id
        self.x = x
        self.y = y
        self.heroes_number = heroes_number
        self.updated_at = updated_at
        self.updated_at_turn = updated_at_turn
        self.created_at = created_at
        self.created_at_turn = created_at_turn
        self.habit_honor = habit_honor
        self.habit_honor_positive = habit_honor_positive
        self.habit_honor_negative = habit_honor_negative
        self.habit_peacefulness = habit_peacefulness
        self.habit_peacefulness_positive = habit_peacefulness_positive
        self.habit_peacefulness_negative = habit_peacefulness_negative
        self.is_frontier = is_frontier
        self.description = description
        self.race = race
        self.persons_changed_at_turn = persons_changed_at_turn
        self.power = power
        self.attrs = attrs
        self.utg_name = utg_name
        self.races = races
        self.nearest_cells = nearest_cells
        self.effects = effects
        self.modifier = modifier

    @property
    def updated_at_game_time(self): return GameTime(*f.turns_to_game_time(self.updated_at_turn))

    @property
    def is_new(self):
        return (datetime.datetime.now() - self.created_at).total_seconds() < conf.settings.NEW_PLACE_LIVETIME

    @property
    def new_for(self):
        return self.created_at + datetime.timedelta(seconds=conf.settings.NEW_PLACE_LIVETIME)

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy

    def sync_modifier(self):
        if self.modifier and not self.modifier.is_enough_power:
            old_modifier = self.modifier
            self.modifier = None
            signals.place_modifier_reseted.send(self.__class__, place=self, old_modifier=old_modifier)

    @property
    def description_html(self): return bbcode.render(self.description)

    def linguistics_restrictions(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage

        restrictions = [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.RACE, self.race.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR, self.habit_honor.interval.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS, self.habit_honor.interval.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.TERRAIN, self.terrain.value).id]

        if self.modifier:
            restrictions.extend(self.modifier.TYPE.linguistics_restrictions())

        return tuple(restrictions)

    @property
    def depends_from_all_heroes(self):
        return self.is_frontier

    def update_heroes_number(self):
        from the_tale.game.heroes.preferences import HeroPreferences
        self.heroes_number = HeroPreferences.count_citizens_of(self, all=self.depends_from_all_heroes)

    def update_heroes_habits(self):
        from the_tale.game.heroes.preferences import HeroPreferences

        habits_values = HeroPreferences.count_habit_values(self, all=self.depends_from_all_heroes)

        self.habit_honor_positive = habits_values[0][0]
        self.habit_honor_negative = habits_values[0][1]
        self.habit_peacefulness_positive = habits_values[1][0]
        self.habit_peacefulness_negative = habits_values[1][1]

    @classmethod
    def _habit_change_speed(cls, current_value, positive, negative):
        positive = abs(positive)
        negative = abs(negative)

        if positive < negative:
            if positive < 0.0001:
                result = -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM
            else:
                result = -min(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, negative / positive)
        elif positive > negative:
            if negative < 0.0001:
                result = c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM
            else:
                result = min(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, positive / negative)
        else:
            result = 0

        return result - c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM_PENALTY * (float(current_value) / c.HABITS_BORDER)

    @property
    def habit_honor_change_speed(self):
        return self._habit_change_speed(self.habit_honor.raw_value, self.habit_honor_positive, self.habit_honor_negative)

    @property
    def habit_peacefulness_change_speed(self):
        return self._habit_change_speed(self.habit_peacefulness.raw_value, self.habit_peacefulness_positive, self.habit_peacefulness_negative)

    def sync_habits(self):
        self.habit_honor.change(self.habit_honor_change_speed)
        self.habit_peacefulness.change(self.habit_peacefulness_change_speed)

    def can_habit_event(self):
        return random.uniform(0, 1) < c.PLACE_HABITS_EVENT_PROBABILITY

    @property
    def persons(self):
        from the_tale.game.persons import storage as persons_storage
        return sorted((person for person in persons_storage.persons.all() if person.place_id == self.id), key=lambda p: -p.power)

    @property
    def total_persons_power(self): return sum([person.power for person in self.persons])

    @property
    def modifiers(self):
        return sorted([modifier(self) for modifier in modifiers.MODIFIERS.values()], key=lambda m: -m.power)

    def mark_as_updated(self): self.updated_at_turn = TimePrototype.get_current_turn_number()

    # def add_person(self):
    #     from the_tale.game.persons.relations import PERSON_TYPE
    #     from the_tale.game.persons.prototypes import PersonPrototype

    #     race = random.choice(RACE.records)
    #     gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

    #     new_person = PersonPrototype.create(place=self,
    #                                         race=race,
    #                                         gender=gender,
    #                                         tp=random.choice(PERSON_TYPE.records),
    #                                         utg_name=names.generator.get_name(race, gender))

    #     signals.place_person_arrived.send(self.__class__, place=self, person=new_person)

    #     return new_person

    # @lazy_property
    # def stability_modifiers(self):
    #     if 'stability_modifiers' not in self.data:
    #         self.data['stability_modifiers'] = []
    #     return self.data['stability_modifiers']


    @property
    def terrain_change_power(self):
        power = self.size
        if self.modifier:
            power = self.modifier.modify_terrain_change_power(power)
        return int(round(power))

    @property
    def terrains(self):
        from the_tale.game.map.storage import map_info_storage
        map_info = map_info_storage.item
        terrains = set()
        for cell in self.nearest_cells:
            terrains.add(map_info.terrain[cell[1]][cell[0]])
        return terrains

    @property
    def terrain(self):
        from the_tale.game.map.storage import map_info_storage
        map_info = map_info_storage.item
        return map_info.terrain[self.y][self.x]

    def sync_race(self):
        self.races.update(persons=self.persons)

        dominant_race = self.races.dominant_race

        if dominant_race and self.race != dominant_race:
            old_race = self.race
            self.race = dominant_race
            signals.place_race_changed.send(self.__class__, place=self, old_race=old_race, new_race=self.race)

    def _effects_generator(self):
        yield effects.Effect(actor_name=u'город', attribute=relations.ATTRIBUTE.STABILITY_RENEWING_SPEED, value=c.PLACE_STABILITY_RECOVER_SPEED)
        yield effects.Effect(actor_name=u'город', attribute=relations.ATTRIBUTE.POLITIC_RADIUS, value=self.attrs.size*1.25)

        for effect in self.effect.effects:
            yield effect

        if self.modifier:
            for effect in self.modifier.effects:
                yield effect

    def effects_generator(self, order):
        for effect in self._effects_generator():
            if effect.attribute.order != order:
                continue
            yield effect

    def refresh_attributes(self):
        self.effects.update_step(self)
        self.attrs.reset()

        orders = sorted(set(record.order for record in relations.ATTRIBUTES))

        for order in orders:
            for effect in self.effects_generator(order):
                effect.apply_to(self)

    # def sync_parameters(self):
    #     self.stability = min(1.0, sum(power[1] for power in self.get_stability_powers()))

    #     self.production = sum(power[1] for power in self.get_production_powers())
    #     self.safety = sum(power[1] for power in self.get_safety_powers())
    #     self.freedom = sum(power[1] for power in self.get_freedom_powers())
    #     self.transport = sum(power[1] for power in self.get_transport_powers())

    #     self.tax = sum(power[1] for power in self.get_tax_powers())

    # def set_expected_size(self, expected_size):
    #     self.expected_size = expected_size

    def get_experience_modifier(self):
        return self.modifier.EXPERIENCE_MODIFIER if self.modifier else 0

    # def _update_powers(self, powers, parameter):
    #     from the_tale.game.places.storage import resource_exchange_storage

    #     for exchange in resource_exchange_storage.get_exchanges_for_place(self):
    #         resource_1, resource_2, place_2 = exchange.get_resources_for_place(self)
    #         if resource_1.parameter == parameter:
    #             powers.append((place_2.name if place_2 is not None else resource_2.text, -resource_1.amount * resource_1.direction))
    #         if resource_2.parameter == parameter:
    #             powers.append((place_2.name if place_2 is not None else resource_1.text, resource_2.amount * resource_2.direction))


    # def get_stability_powers(self):

    #     powers = [ (u'город', 1.0) ]
    #     powers += self.stability_modifiers

    #     stability = sum(power[1] for power in powers)

    #     if stability < places_settings.MIN_STABILITY:
    #         powers.append((u'Серый Орден', places_settings.MIN_STABILITY - stability))


    #     return powers

    # def get_production_powers(self):

    #     powers = [ (u'экономика', f.place_goods_production(self.expected_size)),
    #                (u'потребление', -f.place_goods_consumption(self.size)),
    #                (u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_PRODUCTION_PENALTY)]

    #     if self.get_next_keepers_goods_spend_amount():
    #         powers.append((u'дары Хранителей', self.get_next_keepers_goods_spend_amount()))

    #     self._update_powers(powers, CITY_PARAMETERS.PRODUCTION)

    #     if self.modifier and self.modifier.PRODUCTION_MODIFIER:
    #         powers.append((self.modifier.NAME, self.modifier.PRODUCTION_MODIFIER))

    #     persons_powers = [(person.full_name, person.production) for person in self.persons]
    #     powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
    #     return powers

    # def get_safety_powers(self):
    #     powers = [(u'город', 1.0),
    #               (u'монстры', -c.BATTLES_PER_TURN)]

    #     if self.is_frontier:
    #         powers.append((u'дикие земли', -c.WHILD_BATTLES_PER_TURN_BONUS))

    #     powers.append((u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_SAFETY_PENALTY))

    #     self._update_powers(powers, CITY_PARAMETERS.SAFETY)

    #     if self.modifier and self.modifier.SAFETY_MODIFIER:
    #         powers.append((self.modifier.NAME, self.modifier.SAFETY_MODIFIER))

    #     persons_powers = [(person.full_name, person.safety) for person in self.persons]
    #     powers.extend(sorted(persons_powers, key=lambda p: -p[1]))

    #     safety = sum(power[1] for power in powers)

    #     if safety < places_settings.MIN_SAFETY:
    #         powers.append((u'Серый Орден', places_settings.MIN_SAFETY - safety))

    #     return powers

    # def get_transport_powers(self):
    #     powers = [(u'дороги', 1.0),
    #               (u'трафик', -c.TRANSPORT_FROM_PLACE_SIZE_PENALTY * self.size)]

    #     if self.is_frontier:
    #         powers.append((u'бездорожье', -c.WHILD_TRANSPORT_PENALTY))

    #     powers.append((u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_TRANSPORT_PENALTY))

    #     self._update_powers(powers, CITY_PARAMETERS.TRANSPORT)

    #     if self.modifier and self.modifier.TRANSPORT_MODIFIER:
    #         powers.append((self.modifier.NAME, self.modifier.TRANSPORT_MODIFIER))

    #     persons_powers = [(person.full_name, person.transport) for person in self.persons]
    #     powers.extend(sorted(persons_powers, key=lambda p: -p[1]))

    #     transport = sum(power[1] for power in powers)

    #     if transport < places_settings.MIN_TRANSPORT:
    #         powers.append((u'Серый Орден', places_settings.MIN_TRANSPORT - transport))

    #     return powers

    # def get_freedom_powers(self):
    #     powers = [(u'город', 1.0),
    #               (u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_FREEDOM_PENALTY)]

    #     if self.modifier and self.modifier.FREEDOM_MODIFIER:
    #         powers.append((self.modifier.NAME, self.modifier.FREEDOM_MODIFIER))

    #     persons_powers = [(person.full_name, person.freedom) for person in self.persons]
    #     powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
    #     return powers

    # def get_tax_powers(self):
    #     powers = [(u'город', 0.0)]

    #     self._update_powers(powers, CITY_PARAMETERS.TAX)

    #     return powers

    def cmd_change_power(self, power):
        if amqp_environment.environment.workers.highlevel is None:
            return
        amqp_environment.environment.workers.highlevel.cmd_change_power(power_delta=power,
                                                                        person_id=None,
                                                                        place_id=self.id)


    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'race': self.race.value,
                'name': self.name,
                'size': self.size}
