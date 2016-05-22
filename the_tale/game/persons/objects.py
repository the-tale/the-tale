# coding: utf-8
from utg import words as utg_words
from utg import relations as utg_relations

from the_tale import amqp_environment

from the_tale.common.utils import logic as utils_logic

from the_tale.game import names
from the_tale.game import effects

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c

from the_tale.game.jobs import logic as jobs_logic
from the_tale.game.jobs import effects as jobs_effects

from the_tale.game.places import storage as places_storage
from the_tale.game.places import relations as places_relations


from . import economic
from . import relations


BEST_PERSON_BONUSES = {places_relations.ATTRIBUTE.PRODUCTION: c.PLACE_GOODS_BONUS,
                       places_relations.ATTRIBUTE.FREEDOM: c.PLACE_FREEDOM_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.SAFETY: c.PLACE_SAFETY_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.TRANSPORT: c.PLACE_TRANSPORT_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.STABILITY: c.PLACE_STABILITY_UNIT}



class Person(names.ManageNameMixin2):
    __slots__ = ('id',
                 'created_at_turn',
                 'updated_at_turn',
                 'place_id',
                 'gender',
                 'race',
                 'type',
                 'attrs',
                 'politic_power',

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
                 politic_power,
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
        self.politic_power = politic_power
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
        return u'%s %s-%s' % (self.name, self.race_verbose, self.type.text)

    @property
    def url(self):
        from dext.common.utils.urls import url
        return url('game:persons:show', self.id)


    def name_from(self, with_url=True):
        if with_url:
            return u'<a href="%s" target="_blank">%s</a> — %s из %s' % (self.url, self.name, self.race.text,
                                                                        self.place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE)))

        return u'%s — %s из %s' % (self.name, self.race.text, self.place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE)))

    @property
    def has_building(self): return self.building is not None

    @property
    def building(self): return places_storage.buildings.get_by_person_id(self.id)

    @property
    def on_move_timeout(self):
        return self.seconds_before_next_move > 0

    @property
    def seconds_before_next_move(self):
        return (self.moved_at_turn + c.PERSON_MOVE_DELAY - TimePrototype.get_current_turn_number()) * c.TURN_DELTA


    def cmd_change_power(self, hero_id, has_place_in_preferences, has_person_in_preferences, power):
        if amqp_environment.environment.workers.highlevel is None:
            return

        amqp_environment.environment.workers.highlevel.cmd_change_power(hero_id=hero_id,
                                                                        has_place_in_preferences=has_place_in_preferences,
                                                                        has_person_in_preferences=has_person_in_preferences,
                                                                        power_delta=power,
                                                                        person_id=self.id,
                                                                        place_id=None)

    def linguistics_restrictions(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage

        return (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.GENDER, self.gender.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.RACE, self.race.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.PERSON_TYPE, self.type.value).id)

    @property
    def total_politic_power_fraction(self):
        return self.politic_power.total_politic_power_fraction([person.politic_power for person in self.place.persons])

    @property
    def inner_politic_power_fraction(self):
        return self.politic_power.inner_power_fraction([person.politic_power for person in self.place.persons])

    @property
    def outer_politic_power_fraction(self):
        return self.politic_power.outer_power_fraction([person.politic_power for person in self.place.persons])

    def get_job_power(self):
        return jobs_logic.job_power(objects_number=len(self.place.persons), power=self.total_politic_power_fraction) + self.attrs.job_power_bonus

    def update_job(self):
        from . import logic

        if not self.job.is_completed():
            return ()

        job_effect = self.job.get_apply_effect_method()

        after_update_operations = job_effect(**self.politic_power.job_effect_kwargs(self))

        job_effects_priorities = self.job_effects_priorities()
        if self.job.effect in job_effects_priorities:
            del job_effects_priorities[self.job.effect]

        new_effect = utils_logic.random_value_by_priority(job_effects_priorities.items())

        self.job.new_job(new_effect, normal_power=logic.NORMAL_PERSON_JOB_POWER)

        return after_update_operations


    @property
    def economic_attributes(self):
        return economic.PROFESSION_TO_ECONOMIC[self.type]

    @property
    def specialization_attributes(self):
        return economic.PROFESSION_TO_SPECIALIZATIONS[self.type]

    def job_effects_priorities(self):
        effects_priorities = {}

        for effect in jobs_effects.EFFECT.records:
            effects_priorities[effect] = self.attrs.job_group_priority.get(effect.group, 0)

            if not effect.group.is_ON_PLACE:
                # 0.3 - примерное значение чуть выше средних показателей влияния мастера на базовые аттрибуты города
                # чтобы занятия для героев и для города имели примерно одинаковый приоритет
                # но даже 0.3 сдвигает приоритет в сторону геройских занятий
                effects_priorities[effect] += 0.3

        for attribute in places_relations.ATTRIBUTE.records:
            effect_name = 'PLACE_{}'.format(attribute.name)
            effect = jobs_effects.EFFECT.index_name.get(effect_name)
            if effect:
                effects_priorities[effect] += self.economic_attributes[attribute]

        return {effect: effects_priorities[effect]
                for effect in jobs_effects.EFFECT.records
                if effects_priorities.get(effect, 0) > 0 }


    @classmethod
    def form_choices(cls, choosen_person=None, predicate=lambda place, person: True):
        choices = []

        for place in places_storage.places.all():
            accepted_persons = filter(lambda person: predicate(place, person), place.persons) # pylint: disable=W0110

            if choosen_person is not None and choosen_person.place.id == place.id:
                if choosen_person.id not in [p.id for p in accepted_persons]:
                    accepted_persons.append(choosen_person)

            persons = tuple( (person.id, u'%s [%s %.2f%%]' % (person.name,
                                                              person.type.text,
                                                              person.total_politic_power_fraction * 100 if person.total_politic_power_fraction > 0.001 else 0))
                             for person in accepted_persons )

            persons = sorted(persons, key=lambda choice: choice[1])

            choices.append( ( place.name, persons ) )

        return sorted(choices, key=lambda choice: choice[0])

    def get_economic_modifier(self, attribute):
        return self.economic_attributes[attribute] * BEST_PERSON_BONUSES[attribute]

    def get_economic_modifiers(self):
        for attribute in self.economic_attributes.iterkeys():
            yield attribute, self.get_economic_modifier(attribute)

    def ui_info(self):
        return {'id': self.id,
                'name': self.name,
                'race': self.race.value,
                'gender': self.gender.value,
                'profession': self.type.value,
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


    def place_effects(self):
        for attribute, modifier in self.get_economic_modifiers():
            yield effects.Effect(name=self.name, attribute=attribute, value=modifier)

        for specialization, points in self.specialization_attributes.iteritems():
            if specialization.points_attribute is None:
                continue
            MAX_PERSON_POINTS = 100
            yield effects.Effect(name=self.name,
                                 attribute=specialization.points_attribute,
                                 value=MAX_PERSON_POINTS * points * self.total_politic_power_fraction * self.place.attrs.modifier_multiplier)

        if self.attrs.terrain_radius_bonus != 0:
            yield effects.Effect(name=self.name, attribute=places_relations.ATTRIBUTE.TERRAIN_RADIUS, value=self.attrs.terrain_radius_bonus)

        if self.attrs.politic_radius_bonus != 0:
            yield effects.Effect(name=self.name, attribute=places_relations.ATTRIBUTE.POLITIC_RADIUS, value=self.attrs.politic_radius_bonus)

        if self.attrs.stability_renewing_bonus != 0:
            yield effects.Effect(name=self.name, attribute=places_relations.ATTRIBUTE.STABILITY_RENEWING_SPEED, value=self.attrs.stability_renewing_bonus)


    def refresh_attributes(self):
        self.attrs.reset()

        for effect in self.all_effects():
            effect.apply_to(self.attrs)




class SocialConnection(object):
    __slots__ = ('id', 'connection', 'person_1_id', 'person_2_id', 'created_at', 'created_at_turn', 'state')

    def __init__(self, id, connection, person_1_id, person_2_id, created_at, created_at_turn, state):
        self.id = id
        self.created_at = created_at
        self.created_at_turn = created_at_turn

        self.person_1_id = person_1_id
        self.person_2_id = person_2_id

        self.connection = connection
        self.state = state

    @property
    def persons(self):
        from the_tale.game.persons import storage
        return (storage.persons[self.person_1_id], storage.persons[self.person_2_id])
