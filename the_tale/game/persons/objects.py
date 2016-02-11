# coding: utf-8
import random

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale import amqp_environment

from the_tale.common.utils import logic as utils_logic

from the_tale.game import names

from the_tale.game.balance import constants as c

from the_tale.game.jobs import logic as jobs_logic

from the_tale.game.places import storage as places_storage
from the_tale.game.places import relations as places_relations

from the_tale.game.jobs import effects as jobs_effects

from . import economic


BEST_PERSON_BONUSES = {places_relations.ATTRIBUTE.PRODUCTION: c.PLACE_GOODS_BONUS,
                       places_relations.ATTRIBUTE.FREEDOM: c.PLACE_FREEDOM_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.SAFETY: c.PLACE_SAFETY_FROM_BEST_PERSON,
                       places_relations.ATTRIBUTE.TRANSPORT: c.PLACE_TRANSPORT_FROM_BEST_PERSON}



class Person(names.ManageNameMixin2):
    __slots__ = ('id',
                 'created_at_turn',
                 'place_id',
                 'gender',
                 'race',
                 'type',
                 'politic_power',

                 'friends_number',
                 'enemies_number',

                 'job',

                 'utg_name',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')


    def __init__(self, id, created_at_turn, place_id, gender, race, type, friends_number, enemies_number, politic_power, utg_name, job):
        self.id = id
        self.created_at_turn = created_at_turn
        self.place_id = place_id
        self.gender = gender
        self.race = race
        self.type = type
        self.friends_number = friends_number
        self.enemies_number = enemies_number
        self.politic_power = politic_power
        self.utg_name = utg_name
        self.job = job


    @property
    def place(self): return places_storage.places[self.place_id]

    @property
    def full_name(self):
        return u'%s %s-%s' % (self.name, self.race_verbose, self.type.text)

    @property
    def name_from(self):
        return u'%s — %s из %s' % (self.name, self.race_verbose, self.place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE)))

    @property
    def has_building(self): return places_storage.buildings.get_by_person_id(self.id) is not None

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

    def update_friends_number(self):
        from the_tale.game.heroes.preferences import HeroPreferences
        self.friends_number = HeroPreferences.count_friends_of(self, all=self.place.is_frontier)

    def update_enemies_number(self):
        from the_tale.game.heroes.preferences import HeroPreferences
        self.enemies_number = HeroPreferences.count_enemies_of(self, all=self.place.is_frontier)

    @property
    def total_politic_power_fraction(self):
        # находим минимальное отрицательное влияние и компенсируем его при расчёте долей
        minimum_outer_power = 0.0
        minimum_inner_power = 0.0

        for person in self.place.persons:
            minimum_outer_power = min(minimum_outer_power, person.politic_power.outer_power)
            minimum_inner_power = min(minimum_inner_power, person.politic_power.inner_power)

        total_outer_power = 0.0
        total_inner_power = 0.0

        for person in self.place.persons:
            total_outer_power += (person.politic_power.outer_power - minimum_outer_power)
            total_inner_power += (person.politic_power.inner_power - minimum_inner_power)

        outer_power = (self.politic_power.outer_power / total_outer_power) if total_outer_power else 0
        inner_power = (self.politic_power.inner_power / total_inner_power) if total_inner_power else 0

        return (outer_power + inner_power) / 2

    def get_job_power(self):
        return jobs_logic.job_power(objects_number=len(self.place.persons), power=self.total_politic_power_fraction)

    def give_job_power(self, power):
        from . import logic

        job_effect = self.job.give_power(power)

        if job_effect:
            job_effect(**self.job_effect_kwargs(self))
            self.job.new_job(self.choose_job_effect(), normal_power=logic.NORMAL_PERSON_JOB_POWER)


    def choose_job_effect(self):
        effects_priorities = {}

        for effect in jobs_effects.EFFECT.records:
            if effect.group.is_ON_PLACE:
                effects_priorities[effect] = 0
            else:
                effects_priorities[effect] = 1.0

        for attribute in places_relations.ATTRIBUTE.records:
            effect_name = 'PLACE_{}'.format(attribute.name)
            effect = jobs_effects.EFFECT.index_NAME.get(effect_name)
            if effect:
                effects_priorities[effect] += economic.PROFESSION_TO_ECONOMIC[self.type][attribute]

        effect_group = random.choice(jobs_effects.EFFECT_GROUP.records)

        effects_choices = [(effect, effects_priorities[effect])
                           for effect in jobs_effects.EFFECT.records
                           if effect.group == effect_group and effects_priorities.get(effect, 0) > 0]

        return utils_logic.random_value_by_priority(effects_choices)


    @classmethod
    def form_choices(cls, only_weak=False, choosen_person=None, predicate=lambda place, person: True):
        choices = []

        for place in places_storage.places.all():
            persons_choices = filter(lambda person: predicate(place, person), place.persons) # pylint: disable=W0110
            accepted_persons = persons_choices[min(1, len(place.persons)/2):] if only_weak else persons_choices

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
        return economic.PROFESSION_TO_ECONOMIC[self.type][attribute] * BEST_PERSON_BONUSES[attribute]

    def get_economic_modifiers(self):
        for attribute in economic.PROFESSION_TO_ECONOMIC[self.type].iterkeys():
            yield attribute, self.get_economic_modifier(attribute)

    def ui_info(self):
        return {'id': self.id,
                'name': self.name,
                'race': self.race.value,
                'gender': self.gender.value,
                'profession': self.type.value,
                'place': self.place.id}



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
