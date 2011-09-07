# coding: utf-8

class Environment(object):

    def __init__(self):
        self.places_number = 0
        self.persons_number = 0
        self.items_number = 0

    def new_place(self):
        self.places_number += 1
        return 'place_%d' % self.places_number

    def new_person(self):
        self.persons_number += 1
        return 'person_%d' % self.persons_number

    def new_item(self):
        self.items_number += 1
        return 'item_%d' % self.items_number


class LocalEnvironment(object):

    def __init__(self):
        self.storage = {}

    def register(self, name, value):
        self.storage[name] = value

    def __getattr__(self, name):
        return self.storage[name]
