# coding: utf-8
import time
import datetime

from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests.conf import quests_settings


class QuestsContainer(object):

    __slots__ = ('updated', 'quests_list', 'history', 'interfered_persons', 'hero', '_ui_info')

    def __init__(self):
        self.quests_list = []
        self.history = {}
        self.interfered_persons = {}
        self.hero = None

        self.mark_updated()

    def mark_updated(self):
        self.updated = True
        self._ui_info = None

    def serialize(self):
        return {'quests': [quest.serialize() for quest in self.quests_list],
                'history': self.history,
                'interfered_persons': self.interfered_persons}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.quests_list = [QuestPrototype.deserialize(data=quest_data) for quest_data in data.get('quests', [])]
        obj.history = data.get('history', {})
        obj.interfered_persons = {int(person_id): person_time for person_id, person_time in data.get('interfered_persons', {}).iteritems()}
        return obj

    def initialize(self, hero):
        self.hero = hero
        for quest in self.quests_list:
            quest.hero = hero

    def ui_info(self, hero):
        if self._ui_info is None:
            self._ui_info = self._get_ui_info(hero)

        return self._ui_info


    def _get_ui_info(self, hero):
        spending_ui_info = QuestPrototype.next_spending_ui_info(hero.next_spending)

        if self.has_quests:
            return {'quests': [spending_ui_info] + [quest.ui_info() for quest in self.quests_list]}

        return {'quests': [spending_ui_info, QuestPrototype.no_quests_ui_info(in_place=hero.position.place is not None)]}

    def push_quest(self, quest):
        self.mark_updated()
        self.hero.actions.request_replane()
        self.quests_list.append(quest)

    def pop_quest(self):
        self.mark_updated()
        self.hero.actions.request_replane()
        return self.quests_list.pop()

    @property
    def current_quest(self): return self.quests_list[-1]

    @property
    def min_quest_created_time(self):
        if self.has_quests:
            return min(quest.created_at for quest in self.quests_list)
        return datetime.datetime.now()

    @property
    def has_quests(self): return len(self.quests_list)

    @property
    def number(self): return len(self.quests_list)

    def update_history(self, quest_type, turn_number):
        self.history[quest_type] = turn_number
        self.mark_updated()


    def add_interfered_person(self, person_id):
        self.interfered_persons[person_id] = time.time()

    def is_person_interfered(self, person_id):
        if person_id not in self.interfered_persons:
            return False
        return self.interfered_persons[person_id] + quests_settings.INTERFERED_PERSONS_LIVE_TIME > time.time()

    def get_interfered_persons(self):
        return [person_id for person_id in self.interfered_persons.iterkeys() if self.is_person_interfered(person_id)]

    def sync_interfered_persons(self):
        to_remove = set()
        current_time = time.time()

        for person_id, person_time in self.interfered_persons.iteritems():
            if current_time > person_time + quests_settings.INTERFERED_PERSONS_LIVE_TIME:
                to_remove.add(person_id)

        for person_id in to_remove:
            del self.interfered_persons[person_id]

    def excluded_quests(self, max_number):
        excluded_quests = []
        last_quests = sorted(self.history.iteritems(), key=lambda item: -item[1])
        for last_quest in last_quests[:max_number]: # exclude half of the quests
            excluded_quests.append(last_quest[0])

        return excluded_quests
