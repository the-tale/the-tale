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
        self.lines_number = 0
        self.choices_number = 0

        self.places = {}
        self.persons = {}
        self.items = {}
        self.quests = {}
        self.lines = {}
        self.quests_to_writers = {}
        self.choices = {}
        self.persons_power_points = {}

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

    def new_choice_point(self):
        self.choices_number += 1
        choice = 'choice_%d' % self.choices_number
        self.choices[choice] = {'external_data': {}}
        return choice

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

    def new_line(self, line):
        self.lines_number += 1
        line_id = 'line_%d' % self.lines_number
        self.lines[line_id] = line
        return line_id

    @property
    def root_quest(self): return self.quests[self._root_quest]

    def create_lines(self):
        self.root_quest.create_line(self)

    def get_start_pointer(self):
        return self.root_quest.get_start_pointer()

    def increment_pointer(self, pointer, choices):
        return self.root_quest.increment_pointer(self, pointer, choices)

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

    def get_nearest_quest_choice(self, pointer):

        tmp_pointer = copy.deepcopy(pointer)

        while tmp_pointer:
            cmd = self.get_command(tmp_pointer)

            if len(tmp_pointer) != len(pointer):
                return None

            if hasattr(cmd, 'choices'):
                return cmd

            tmp_pointer = self.increment_pointer(tmp_pointer, {})

        return None


    def get_writer(self, pointer):
        quest = self.get_quest(pointer)
        writer = self.writers_source.writers[self.quests_to_writers[quest.id]](self, quest.env_local)
        return writer

    def percents(self, pointer):
        return self.root_quest.get_percents(self, pointer)

    def serialize(self):
        return { 'numbers': { 'items_number': self.items_number,
                              'choices_number': self.choices_number},
                 'places': self.places,
                 'persons': self.persons,
                 'items': self.items,
                 'choices': self.choices,
                 'quests': dict( (quest_id, quest.serialize() ) 
                                 for quest_id, quest in self.quests.items() ),
                 'lines': dict( (line_id, line.serialize() ) 
                                 for line_id, line in self.lines.items() ),
                 'root_quest': self._root_quest,
                 'quests_to_writers': self.quests_to_writers,
                 'persons_power_points': self.persons_power_points}

    def deserialize(self, data):
        from .quest_line import Line

        self.items_number = data['numbers']['items_number']
        self.choices_number = data['numbers'].get('choices_number', 0)
        self.places = data['places']
        self.persons = data['persons']
        self.items = data['items']
        self.choices = data.get('choices', {})

        self.quests = dict( (quest_id, self.quests_source.deserialize_quest(quest_data)) 
                            for quest_id, quest_data in data['quests'].items())

        for line_id, line_data in data['lines'].items():
            line = Line()
            line.deserialize(line_data)
            self.lines[line_id] = line

        self._root_quest = data['root_quest']

        self.quests_to_writers = data['quests_to_writers']
        self.persons_power_points = data.get('persons_power_points', {})


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
