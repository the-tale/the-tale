# coding: utf-8
import time

from the_tale.game.balance import constants as c

from the_tale.game.prototypes import TimePrototype, GameTime

from the_tale.game.heroes.conf import heroes_settings


class MessageSurrogate(object):
    __slots__ = ('turn_number', 'timestamp', 'key', 'externals', '_ui_info', '_message')

    def __init__(self, turn_number, timestamp, key, externals, message):
        self.turn_number = turn_number
        self.timestamp = timestamp
        self.key = key
        self.externals = externals

        self._ui_info = None
        self._message = message


    @classmethod
    def create(cls, key, externals, turn_delta=0):
        return cls(turn_number=TimePrototype.get_current_turn_number()+turn_delta,
                   timestamp=time.time()+turn_delta*c.TURN_DELTA,
                   key=key,
                   externals=externals,
                   message=None)

    def serialize(self):
        return (self.turn_number, self.timestamp, self.message)

    @classmethod
    def deserialize(cls, data):
        return cls(turn_number=data[0],
                   timestamp=data[1],
                   message=data[2],
                   key=None,
                   externals=None)

    @property
    def message(self):
        from the_tale.linguistics.logic import render_text

        if self._message is not None:
            return self._message

        self._message = render_text(lexicon_key=self.key, externals=self.externals)

        return self._message


    def ui_info(self, with_date=False):
        if self._ui_info is not None:
            return self._ui_info

        game_time = GameTime.create_from_turn(self.turn_number)

        if with_date:
            self._ui_info = (self.timestamp, game_time.verbose_time, self.message, game_time.verbose_date)
        else:
            self._ui_info = (self.timestamp, game_time.verbose_time, self.message)

        return self._ui_info

    def clone(self):
        return self.__class__(turn_number=self.turn_number,
                              timestamp=self.timestamp,
                              key=self.key,
                              externals=self.externals,
                              message=self._message)


def _message_key(m): return (m.turn_number, m.timestamp)

class MessagesContainer(object):

    __slots__ = ('messages', 'updated')

    MESSAGES_LOG_LENGTH = None

    def __init__(self):
        self.messages = []
        self.updated = False

    def push_message(self, msg):
        self.updated = True

        self.messages.append(msg)

        if len(self.messages) > 1 and (self.messages[-1].turn_number < self.messages[-2].turn_number or self.messages[-1].timestamp < self.messages[-2].timestamp):
            self.messages.sort(key=_message_key) # compare tuples

        if len(self.messages) > self.MESSAGES_LOG_LENGTH:
            self.messages.pop(0)

    def messages_number(self):
        return len(self.messages)

    def clear(self):
        if self.messages:
            del self.messages[:]
            self.updated = True

    def __len__(self): return len(self.messages)


    def ui_info(self, with_date=False):
        current_turn = TimePrototype.get_current_turn_number()

        messages = []

        for message in self.messages:
            if message.turn_number > current_turn:
                break

            messages.append(message.ui_info(with_date=with_date))

        return messages

    def serialize(self):
        return {'messages': [message.serialize() for message in self.messages]}

    @classmethod
    def deserialize(cls, hero, data):
        obj = cls()
        obj.messages = [MessageSurrogate.deserialize(message_data) for message_data in data['messages']]
        return obj

    def __eq__(self, other):
        if len(self.messages) != len(other.messages):
            return False

        for a, b in zip(self.messages, other.messages):
            if a.turn_number != b.turn_number or a.message != b.message or abs(a.timestamp - b.timestamp) > 0.0001:
                return False

        return True


class JournalContainer(MessagesContainer):
    MESSAGES_LOG_LENGTH = heroes_settings.MESSAGES_LOG_LENGTH


class DiaryContainer(MessagesContainer):
    MESSAGES_LOG_LENGTH = heroes_settings.DIARY_LOG_LENGTH
