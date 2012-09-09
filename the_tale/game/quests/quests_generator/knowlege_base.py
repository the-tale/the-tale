# coding: utf-8
import copy
import random

UNDEFINED_PLACE = 'undefined_place'

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

    def add_place(self, uuid, terrain=None, external_data={}):
        if uuid in self.places:
            raise QuestGeneratorException(u'place "%s" has already added to base' % uuid)

        self.places[uuid] = {'uuid': uuid,
                             'terrain': terrain,
                             'external_data': external_data,
                             'persons': set()}

    def add_person(self, uuid, place=UNDEFINED_PLACE, external_data={}):
        if uuid in self.persons:
            raise QuestGeneratorException(u'person "%s" has already added to base' % uuid)
        self.persons[uuid] = {'uuid': uuid,
                              'external_data': external_data,
                              'place': place}

    def get_special(self, uuid):
        return self.specials.get(uuid, None)

    def get_random_place(self, terrain=None, exclude=[]):

        choices = [uuid
                   for uuid, data in self.places.items()
                   if (uuid not in exclude and
                       (terrain is None or data['terrain'] in terrain))]

        if len(choices) == 0:
            raise RollBackException('can not found suitable place with terrain: %r, excludes: %r' % (terrain, exclude))

        return random.choice(choices)

    def get_random_person(self, place=UNDEFINED_PLACE, exclude=[]):

        exclude = set(exclude)

        choices = [ person_uuid for person_uuid in self.places[place]['persons'] if person_uuid not in exclude]

        if len(choices) == 0:
            raise RollBackException('can not found suitable person for place: %s with excludes: %r' % (place, exclude))

        return random.choice(choices)
