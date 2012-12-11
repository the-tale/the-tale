# coding: utf-8
import copy
import random

from game.quests.quests_generator.exceptions import QuestGeneratorException, RollBackException

class KnowlegeBase(object):

    def __init__(self):
        self.places = {}
        self.persons = {}
        self.specials = {}

    def initialize(self):
        for person_uuid, person in self.persons.items():
            if person['place'] not in self.places:
                raise QuestGeneratorException(u'place "%s" for person "%s" does not added to base' % (person['place'], person_uuid))
            self.places[person['place']]['persons'].add(person_uuid)

    def add_special(self, uuid, value):
        if uuid in self.specials:
            raise QuestGeneratorException(u'special "%s" has already added to base' % uuid)

        self.specials[uuid] = value

    def add_place(self, uuid, terrains=set(), external_data={}):
        if uuid in self.places:
            raise QuestGeneratorException(u'place "%s" has already added to base' % uuid)

        self.places[uuid] = {'uuid': uuid,
                             'terrains': terrains,
                             'external_data': external_data,
                             'persons': set()}

    def add_person(self, uuid, place=None, profession=None, external_data={}):
        if uuid in self.persons:
            raise QuestGeneratorException(u'person "%s" has already added to base' % uuid)
        self.persons[uuid] = {'uuid': uuid,
                              'profession': profession,
                              'external_data': external_data,
                              'place': place}

    def get_special(self, uuid):
        return self.specials.get(uuid, None)

    def get_random_place(self, terrain=None, exclude=[]):
        choices = [uuid
                   for uuid, data in self.places.items()
                   if (uuid not in exclude and
                       (terrain is None or set(data['terrains']) & set(terrain)))]

        if len(choices) == 0:
            raise RollBackException('can not found suitable place with terrain: %r, excludes: %r' % (terrain, exclude))

        return random.choice(choices)

    def get_random_person(self, place=None, profession=None, exclude=[]):

        exclude = set(exclude)

        choices = [person_uuid for person_uuid in self.persons.keys() if person_uuid not in exclude]

        if place is not None:
            choices = [ person_uuid for person_uuid in self.places[place]['persons'] if person_uuid in choices]

        if profession is not None:
            choices = [ person_uuid for person_uuid in choices if self.persons[person_uuid]['profession'] == profession]

        if len(choices) == 0:
            raise RollBackException('can not found suitable person for place: %s with excludes: %r, profession: %s' % (place, exclude, profession))

        return random.choice(choices)
