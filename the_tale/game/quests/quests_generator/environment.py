# coding: utf-8
import random
import copy

class RollBackException(Exception): pass

class BaseEnvironment(object):

    def __init__(self, quests_source, writers_source, knowlege_base):
        self.quests_source = quests_source
        self.writers_source = writers_source
        self.knowlege_base = knowlege_base

        self.items_number = 0
        self.quests_number = 0

        self.places = {}
        self.persons = {}
        self.items = {}
        self.quests = {}
        self.quests_to_writers = {}

        self._root_quest = None
        
    def new_place(self, place_uuid=None):
        if not place_uuid:
            place_uuid = self.knowlege_base.get_random_place(exclude=self.places.keys())

        place = self.knowlege_base.places[place_uuid]
        self.places[place_uuid] = {'external_data': copy.deepcopy(place['external_data'])}
        return place_uuid

    def new_person(self, from_place, person_uuid=None):
        if not person_uuid:
            person_uuid = self.knowlege_base.get_random_person(place=from_place, exclude=self.persons.keys())

        person = self.knowlege_base.persons[person_uuid]
        self.persons[person_uuid] = {'external_data': copy.deepcopy(person['external_data'])}
        return person_uuid

    def new_item(self):
        self.items_number += 1
        item = 'item_%d' % self.items_number
        self.items[item] = {'external_data': {}}
        return item

    def new_quest(self, place_start=None, person_start=None):
        self.quests_number += 1
        quest_id = 'quest_%d' % self.quests_number

        if self._root_quest is None:
            self._root_quest = quest_id

        quest = random.choice(self.quests_source.quests_list)()

        quest.initialize(quest_id,
                         self,
                         place_start=place_start, 
                         person_start=person_start)

        self.quests[quest_id] = quest
        self.quests_to_writers[quest_id] = random.choice(self.writers_source.quest_writers[quest.type()]).type()
        
        return quest_id

    @property
    def root_quest(self): return self.quests[self._root_quest]

    def create_lines(self):
        self.root_quest.create_line(self)

    def get_start_pointer(self):
        return self.root_quest.get_start_pointer()

    def increment_pointer(self, pointer):
        return self.root_quest.increment_pointer(self, pointer)

    def get_quest(self, pointer):
        return self.root_quest.get_quest(self, pointer)

    def get_command(self, pointer):
        return self.root_quest.get_command(self, pointer)

    def get_writers_text_chain(self, pointer):
        chain = self.root_quest.get_quest_action_chain(self, pointer)

        writers_chain = []

        for quest, command in chain:
            writer = self.writers_source.writers[self.quests_to_writers[quest.id]](self, quest.env_local)
            writers_chain.append({'quest_type': quest.type(),
                                  'quest_text': writer.get_action_msg('quest_description'),
                                  'action_type': command.type(),
                                  'action_text': writer.get_action_msg(command.event)})
        
        return writers_chain

    def get_writer(self, pointer):
        quest = self.get_quest(pointer)
        writer = self.writers_source.writers[self.quests_to_writers[quest.id]](self, quest.env_local)
        return writer

    def percents(self, pointer):
        return self.root_quest.get_percents(self, pointer)

    def serialize(self):
        return { 'numbers': { 'items_number': self.items_number},
                 'places': self.places,
                 'persons': self.persons,
                 'items': self.items,
                 'quests': dict( (quest_id, quest.serialize() ) 
                                 for quest_id, quest in self.quests.items() ),
                 'root_quest': self._root_quest,
                 'quests_to_writers': self.quests_to_writers }

    def deserialize(self, data):
        self.items_number = data['numbers']['items_number']
        self.places = data['places']
        self.persons = data['persons']
        self.items = data['items']

        self.quests = dict( (quest_id, self.quests_source.deserialize_quest(quest_data)) 
                            for quest_id, quest_data in data['quests'].items())

        self._root_quest = data['root_quest']

        self.quests_to_writers = data['quests_to_writers']


class LocalEnvironment(object):

    def __init__(self, data=None):
        self.storage = {}

    def register(self, name, value):
        self.storage[name] = value

    def get_data(self):
        return copy.deepcopy(self.storage)

    def __getattr__(self, name):
        if name in self.storage:
            return self.storage[name]
        raise AttributeError('LocalEnvironment object does not contain value "%s"' % name)

    def serialize(self):
        return self.storage

    def deserialize(self, data):
        self.storage = data
