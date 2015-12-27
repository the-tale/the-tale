# coding: utf-8

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale import amqp_environment

from the_tale.game import names

from the_tale.game.places import storage as places_storage


class PersonPrototype(names.ManageNameMixin2):
    __slots__ = ('id',
                 'created_at_turn',
                 'place_id',
                 'gender',
                 'race',
                 'type',
                 'state',
                 'power',

                 'friends_number',
                 'enemies_number',

                 'utg_name',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')


    def __init__(self, id, created_at_turn, place_id, gender, race, type, state, friends_number, enemies_number, power, utg_name):
        self.id = id
        self.created_at_turn = created_at_turn
        self.place_id = place_id
        self.gender = gender
        self.race = race
        self.type = type
        self.state = state
        self.friends_number = friends_number
        self.enemies_number = enemies_number
        self.power = power
        self.utg_name = utg_name


    @property
    def place(self): return places_storage.places_storage[self.place_id]

    @property
    def full_name(self):
        return u'%s %s-%s' % (self.name, self.race_verbose, self.type.text)

    @property
    def name_from(self):
        return u'%s — %s из %s' % (self.name, self.race_verbose, self.place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE)))

    @property
    def has_building(self): return places_storage.buildings_storage.get_by_person_id(self.id) is not None

    def cmd_change_power(self, power):
        if amqp_environment.environment.workers.highlevel is None:
            return
        amqp_environment.environment.workers.highlevel.cmd_change_power(power_delta=power,
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


    @classmethod
    def form_choices(cls, only_weak=False, choosen_person=None, predicate=lambda place, person: True):
        choices = []

        for place in places_storage.all():
            persons_choices = filter(lambda person: predicate(place, person), place.persons) # pylint: disable=W0110
            accepted_persons = persons_choices[place.max_persons_number/2:] if only_weak else persons_choices

            if choosen_person is not None and choosen_person.place.id == place.id:
                if choosen_person.id not in [p.id for p in accepted_persons]:
                    accepted_persons.append(choosen_person)

            place_power = place.total_persons_power

            persons = tuple( (person.id, u'%s [%s %.2f%%]' % (person.name,
                                                              person.type.text,
                                                              person.power / place_power * 100 if place_power > 0.001 else 0))
                             for person in accepted_persons )

            persons = sorted(persons, key=lambda choice: choice[1])

            choices.append( ( place.name, persons ) )

        return sorted(choices, key=lambda choice: choice[0])


    def ui_info(self):
        return {'id': self.id,
                'name': self.name,
                'race': self.race.value,
                'gender': self.gender.value,
                'profession': self.type.value,
                'mastery_verbose': self.mastery_verbose,
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
        return (storage.persons_storage[self.person_1_id], storage.persons_storage[self.person_2_id])
