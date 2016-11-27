
import datetime
import itertools
import collections


class Message(object):
    __slots__ = ('timestamp', 'turn_number', 'type', 'game_time', 'game_date', 'position', 'message', 'variables')


    def __init__(self, timestamp, turn_number, type, game_time, game_date, position, message, variables):
        self.timestamp = timestamp
        self.turn_number = turn_number
        self.type = type
        self.game_time = game_time
        self.game_date = game_date
        self.position = position
        self.message = message
        self.variables = variables


    def serialize(self):
        return {'timestamp': self.timestamp,
                'turn_number': self.turn_number,
                'type': self.type,
                'game_time': self.game_time,
                'game_date': self.game_date,
                'position': self.position,
                'message': self.message,
                'variables': self.variables}


    @classmethod
    def deserialize(cls, data):
        return cls(**data)


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.timestamp == other.timestamp and
                self.turn_number == other.turn_number and
                self.type == other.type and
                self.game_time == other.game_time and
                self.game_date == other.game_date and
                self.position == other.position and
                self.message == other.message and
                self.variables == other.variables)


    def __ne__(self, other):
        return not self.__eq__(other)



class Diary(object):
    __slots__ = ('_messages', '_counter', 'version')


    def __init__(self):
        self._messages = []
        self._counter = itertools.count()
        self.version = 0


    def push_message(self, message, diary_size=None, increment_version=True):
        self._messages.append((message.turn_number, message.timestamp, next(self._counter), message))
        self._messages.sort()

        if diary_size is not None:
            while len(self._messages) > diary_size:
                self._messages.pop(0)

        if increment_version:
            self.version += 1


    def messages(self):
        for turn_number, timestamp, number, messages in self._messages:
            yield messages


    def __eq__(self, other):
        # do not compare updated_at and _total_messages
        return (self.__class__ == other.__class__ and
                list(self.messages()) == list(other.messages()) and
                self.version == other.version)


    def __ne__(self, other):
        return not self.__eq__(other)
