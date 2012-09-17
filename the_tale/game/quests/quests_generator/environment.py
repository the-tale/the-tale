# coding: utf-8
import random
import copy

from game.quests.quests_generator.exceptions import QuestGeneratorException, RollBackException

class BaseEnvironment(object):

    def __init__(self, writers_constructor, quests_source=None, knowlege_base=None):
        self.quests_source = quests_source
        self.writers_constructor = writers_constructor
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
        self.choices = {}
        self.quests_results = {}
        self.persons_power_points = {}

        self._root_quest = None

    def new_place(self, terrain=None, place_uuid=None, person_uuid=None):

        if person_uuid is not None:
            if person_uuid not in self.knowlege_base.persons:
                raise QuestGeneratorException(u'person "%s" does not registered' % person_uuid)
            place_uuid = self.knowlege_base.persons[person_uuid]['place']

        if not place_uuid:
            place_uuid = self.knowlege_base.get_random_place(terrain=terrain, exclude=self.places.keys())
        else:
            if place_uuid not in self.knowlege_base.places:
                raise QuestGeneratorException(u'place "%s" does not exist in knowlege base' % place_uuid)

        if place_uuid in self.places:
            return place_uuid

        place = self.knowlege_base.places[place_uuid]
        self.places[place_uuid] = {'external_data': copy.deepcopy(place['external_data'])}
        return place_uuid

    def new_person(self, from_place=None, person_uuid=None, profession=None):

        if person_uuid is None:
            if from_place is not None and from_place not in self.places:
                raise QuestGeneratorException(u'place "%s" does not registered' % from_place)

            person_uuid = self.knowlege_base.get_random_person(place=from_place, profession=profession, exclude=self.persons.keys())
        else:
            if person_uuid not in self.knowlege_base.persons:
                raise QuestGeneratorException(u'person "%s" does not exist in knowlege base' % person_uuid)

        if person_uuid in self.persons:
            return person_uuid

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

    def new_quest(self, from_list=None, excluded_list=[], **kwargs):
        self.quests_number += 1
        quest_id = 'quest_%d' % self.quests_number

        if self._root_quest is None:
            self._root_quest = quest_id

        quests_list = self.quests_source.filter(self, from_list=from_list, excluded_list=excluded_list)

        if not quests_list:
            raise RollBackException('can not find suitable quests')

        quest = random.choice(quests_list)()

        quest.initialize(quest_id,
                         self,
                         **kwargs)

        self.quests[quest_id] = quest

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
        self.root_quest.calculate_changes(self, [])
        self.root_quest.calculate_availability(self, blocked_quests_results={}, current_quest_results=set())

    def get_start_pointer(self):
        return self.root_quest.get_start_pointer(self)

    def increment_pointer(self, pointer, choices):
        return self.root_quest.increment_pointer(self, pointer, choices)

    def get_quest(self, pointer):
        return self.root_quest.get_quest(self, pointer)

    def get_command(self, pointer):
        return self.root_quest.get_command(self, pointer)

    def get_writers_text_chain(self, hero, pointer):
        chain = self.root_quest.get_quest_action_chain(self, pointer)

        writers_chain = []

        for quest, command, choices in chain:
            writer = self.writers_constructor(hero, quest.type(), self, quest.env_local)

            quest_choices = []
            for choice_id, choosen_line in choices:
                quest_choices.append(writer.get_choice_result_msg(choice_id, choosen_line))

            writers_chain.append({'quest_type': quest.type(),
                                  'quest_text': writer.get_description_msg(),
                                  'action_type': command.type(),
                                  'action_text': writer.get_action_msg(command.event),
                                  'choices': quest_choices,
                                  'actors': quest.get_actors(self)})


        return writers_chain

    def get_nearest_quest_choice(self, pointer):

        tmp_pointer = copy.deepcopy(pointer)

        while tmp_pointer:

            cmd = self.get_command(tmp_pointer)

            if len(tmp_pointer) != len(pointer):
                return None

            if cmd.is_choice:
                return cmd

            tmp_pointer = self.increment_pointer(tmp_pointer, {})

        return None


    def get_writer(self, hero, pointer):
        quest = self.get_quest(pointer)
        writer = self.writers_constructor(hero, quest.type(), self, quest.env_local)
        return writer

    def percents(self, pointer):
        return self.root_quest.get_percents(self, pointer)

    def serialize(self):
        return { 'numbers': { 'items_number': self.items_number,
                              'choices_number': self.choices_number,
                              'quests_number': self.quests_number,
                              'lines_number': self.lines_number},
                 'places': self.places,
                 'persons': self.persons,
                 'items': self.items,
                 'choices': self.choices,
                 'quests': dict( (quest_id, quest.serialize() )
                                 for quest_id, quest in self.quests.items() ),
                 'lines': dict( (line_id, line.serialize() )
                                 for line_id, line in self.lines.items() ),
                 'root_quest': self._root_quest,
                 'persons_power_points': self.persons_power_points,
                 'quests_results': self.quests_results}

    def deserialize(self, data):

        from .quest_line import Line

        self.items_number = data['numbers']['items_number']
        self.choices_number = data['numbers'].get('choices_number', 0)
        self.quests_number = data['numbers'].get('quests_number', 0)
        self.lines_number = data['numbers'].get('lines_number', 0)
        self.places = data['places']
        self.persons = data['persons']
        self.items = data['items']
        self.choices = data.get('choices', {})
        self.quests_results = data.get('quests_results', {})

        self.quests = dict( (quest_id, self.quests_source.deserialize_quest(quest_data))
                            for quest_id, quest_data in data['quests'].items())

        for line_id, line_data in data['lines'].items():
            line = Line()
            line.deserialize(line_data)
            self.lines[line_id] = line

        self._root_quest = data['root_quest']

        self.persons_power_points = data.get('persons_power_points', {})

    def __eq__(self, other):
        return (self.quests_source == other.quests_source and
                self.writers_constructor == other.writers_constructor and
                self.knowlege_base == other.knowlege_base and

                self.items_number == other.items_number and
                self.quests_number == other.quests_number and
                self.lines_number == other.lines_number and
                self.choices_number == other.choices_number and

                self.places == other.places and
                self.persons == other.persons and
                self.items == other.items and
                self.quests == other.quests and
                self.lines == other.lines and
                self.choices == other.choices and
                self.persons_power_points == other.persons_power_points and
                self.quests_results == other.quests_results and

                self._root_quest == other._root_quest)



class LocalEnvironment(object):

    def __init__(self, data=None):
        self._storage = {}

    def register(self, name, value):
        self._storage[name] = value

    def get_data(self):
        return copy.deepcopy(self._storage)

    def __getattr__(self, name):
        if name in self._storage:
            return self._storage[name]
        raise AttributeError('LocalEnvironment object does not contain value "%s"' % name)

    def __getitem__(self, name):
        return self._storage[name]

    def serialize(self):
        return self._storage

    def deserialize(self, data):
        self._storage = data

    def __eq__(self, other):
        return self._storage == other._storage
