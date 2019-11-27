
import smart_imports

smart_imports.all()


BEST_PERSON_BONUSES = {places_relations.ATTRIBUTE.PRODUCTION: c.PLACE_GOODS_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.FREEDOM: c.PLACE_FREEDOM_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.SAFETY: c.PLACE_SAFETY_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.TRANSPORT: c.PLACE_TRANSPORT_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.CULTURE: c.PLACE_CULTURE_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.STABILITY: c.PLACE_STABILITY_FROM_BEST_PERSON}


class Person(game_names.ManageNameMixin2):
    __slots__ = ('id',
                 'created_at_turn',
                 'updated_at_turn',
                 'place_id',
                 'gender',
                 'race',
                 'type',
                 'attrs',

                 'job',

                 'moved_at_turn',

                 'utg_name',

                 'personality_cosmetic',
                 'personality_practical',

                 'updated_at',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 created_at_turn,
                 updated_at_turn,
                 place_id,
                 gender,
                 race,
                 type,
                 utg_name,
                 job,
                 moved_at_turn,
                 attrs,
                 personality_cosmetic,
                 personality_practical,
                 updated_at):
        self.id = id
        self.created_at_turn = created_at_turn
        self.updated_at_turn = updated_at_turn
        self.place_id = place_id
        self.gender = gender
        self.race = race
        self.type = type
        self.utg_name = utg_name
        self.job = job
        self.moved_at_turn = moved_at_turn
        self.attrs = attrs
        self.personality_cosmetic = personality_cosmetic
        self.personality_practical = personality_practical
        self.updated_at = updated_at

    @property
    def place(self):
        return places_storage.places[self.place_id]

    @property
    def full_name(self):
        return '%s %s-%s' % (self.name, self.race_verbose, self.type.text)

    @property
    def url(self):
        return dext_urls.url('game:persons:show', self.id)

    def name_from(self, with_url=True):
        if with_url:
            place_name = self.place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
            return '<a href="%s" target="_blank">%s</a> — %s из %s' % (self.url,
                                                                       self.name,
                                                                       self.race.text,
                                                                       place_name)

        return '%s — %s из %s' % (self.name, self.race.text, self.place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE)))

    @property
    def has_building(self):
        return self.building is not None

    @property
    def building(self):
        return places_storage.buildings.get_by_person_id(self.id)

    @property
    def on_move_timeout(self):
        return self.seconds_before_next_move > 0

    @property
    def seconds_before_next_move(self):
        return (self.moved_at_turn + c.PERSON_MOVE_DELAY - game_turn.number()) * c.TURN_DELTA

    def linguistics_restrictions(self):
        return (linguistics_restrictions.get(game_relations.ACTOR.PERSON),
                linguistics_restrictions.get(self.gender),
                linguistics_restrictions.get(self.race),
                linguistics_restrictions.get(self.type))

    @property
    def economic_attributes(self):
        return economic.PROFESSION_TO_ECONOMIC[self.type]

    @property
    def specialization_attributes(self):
        return economic.PROFESSION_TO_SPECIALIZATIONS[self.type]

    @classmethod
    def form_choices(cls, choosen_person=None, predicate=lambda place, person: True):
        choices = []

        for place in places_storage.places.all():
            accepted_persons = [person for person in place.persons if predicate(place, person)]  # pylint: disable=W0110

            if choosen_person is not None and choosen_person.place.id == place.id:
                if choosen_person.id not in [p.id for p in accepted_persons]:
                    accepted_persons.append(choosen_person)

            persons = tuple((person.id, '%s [%s %.2f%%]' % (person.name,
                                                            person.type.text,
                                                            politic_power_storage.persons.total_power_fraction(person.id) * 100 if politic_power_storage.persons.total_power_fraction(person.id) > 0.001 else 0))
                            for person in accepted_persons)

            persons = sorted(persons, key=lambda choice: choice[1])

            choices.append((place.name, persons))

        return sorted(choices, key=lambda choice: choice[0])

    def get_economic_modifier(self, attribute):
        return self.economic_attributes[attribute] / 3.0 * BEST_PERSON_BONUSES[attribute]

    def get_economic_modifiers(self):
        for attribute in self.economic_attributes.keys():
            yield attribute, self.get_economic_modifier(attribute)

    def ui_info(self):
        return {'id': self.id,
                'name': self.name,
                'race': self.race.value,
                'gender': self.gender.value,
                'profession': self.type.value,
                'personality': {'practical': self.personality_practical.value,
                                'cosmetic': self.personality_cosmetic.value},
                'place': self.place.id}

    def _effects_generator(self):
        yield self.personality_cosmetic.effect
        yield self.personality_practical.effect

    def effects_generator(self, order):
        for effect in self._effects_generator():
            if effect.attribute.order != order:
                continue
            yield effect

    def all_effects(self):
        for order in relations.ATTRIBUTE.EFFECTS_ORDER:
            for effect in self.effects_generator(order):
                yield effect

    def modify_specialization_points(self, points):
        return f.place_specialization_from_person(person_points=points,
                                                  politic_power_fraction=politic_power_storage.persons.total_power_fraction(self.id),
                                                  place_size_multiplier=self.place.attrs.modifier_multiplier)

    def specializations_for_ui(self):
        specializations = []

        for specialization, points in self.specialization_attributes.items():
            if specialization.points_attribute is None:
                continue

            specializations.append((specialization.text, self.modify_specialization_points(points)))

        specializations.sort(key=lambda x: -x[1])

        return specializations

    def specialization_effects(self):
        for specialization, points in self.specialization_attributes.items():
            if specialization.points_attribute is None:
                continue

            yield game_effects.Effect(name=self.name,
                                      attribute=specialization.points_attribute,
                                      value=self.modify_specialization_points(points))

    def place_effects(self):
        effect_name = 'Мастер {}'.format(self.name)

        for attribute, modifier in self.get_economic_modifiers():
            yield game_effects.Effect(name=effect_name, attribute=attribute, value=modifier)

        yield from self.specialization_effects()

        if self.attrs.terrain_radius_bonus != 0:
            yield game_effects.Effect(name=effect_name,
                                      attribute=places_relations.ATTRIBUTE.TERRAIN_RADIUS,
                                      value=self.attrs.terrain_radius_bonus)

        if self.attrs.politic_radius_bonus != 0:
            yield game_effects.Effect(name=effect_name,
                                      attribute=places_relations.ATTRIBUTE.POLITIC_RADIUS,
                                      value=self.attrs.politic_radius_bonus)

        if self.attrs.stability_renewing_bonus != 0:
            yield game_effects.Effect(name=effect_name,
                                      attribute=places_relations.ATTRIBUTE.STABILITY_RENEWING_SPEED,
                                      value=self.attrs.stability_renewing_bonus)

        if self.has_building:
            yield game_effects.Effect(name='стабилизация {} ({})'.format(self.building.name, effect_name),
                                      attribute=places_relations.ATTRIBUTE.PRODUCTION,
                                      value=-c.CELL_STABILIZATION_PRICE)

            yield game_effects.Effect(name='ремонт {} ({})'.format(self.building.name, effect_name),
                                      attribute=places_relations.ATTRIBUTE.PRODUCTION,
                                      value=-self.attrs.building_support_cost)

    def refresh_attributes(self):
        self.attrs.reset()

        for effect in self.all_effects():
            effect.apply_to(self.attrs)

    def meta_object(self):
        return meta_relations.Person.create_from_object(self)


class SocialConnection(object):
    __slots__ = ('id', 'connection', 'person_1_id', 'person_2_id', 'created_at', 'created_at_turn')

    def __init__(self, id, connection, person_1_id, person_2_id, created_at, created_at_turn):
        self.id = id
        self.created_at = created_at
        self.created_at_turn = created_at_turn

        self.person_1_id = person_1_id
        self.person_2_id = person_2_id

        self.connection = connection

    @property
    def persons(self):
        return (storage.persons[self.person_1_id], storage.persons[self.person_2_id])

    def can_be_removed(self):
        return game_turn.number() >= self.created_at_turn + c.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME
