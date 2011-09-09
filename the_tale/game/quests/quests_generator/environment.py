# coding: utf-8

class BaseEnvironment(object):

    def __init__(self, data=None):
        self.places_number = 0
        self.persons_number = 0
        self.items_number = 0

        self.places = {}
        self.persons = {}
        self.items = {}
        
        if data:
            self.load_from_dict(data)

    def new_place(self):
        self.places_number += 1
        place = 'place_%d' % self.places_number
        self.places[place] = {'info': {},
                              'game': {}}
        return place

    def new_person(self):
        self.persons_number += 1
        person = 'person_%d' % self.persons_number
        self.persons[person] = {'info': {},
                                'game': {}}
        return person

    def new_item(self):
        self.items_number += 1
        item = 'item_%d' % self.items_number
        self.items[item] = {'info': {},
                            'game': {}}
        return item

    def save_to_dict(self):
        return { 'numbers': { 'places_number': self.places_number,
                              'persons_number': self.persons_number,
                              'items_number': self.items_number},
                 'places': self.places,
                 'persons': self.persons,
                 'items': self.items }

    def load_from_dict(self, data):
        self.places_number = data['numbers']['places_number']
        self.persons_number = data['numbers']['persons_number']
        self.items_number = data['numbers']['items_number']
        self.places = data['places']
        self.persons = data['persons']
        self.items = data['items']


class LocalEnvironment(object):

    def __init__(self):
        self.storage = {}

    def register(self, name, value):
        self.storage[name] = value

    def __getattr__(self, name):
        return self.storage[name]
