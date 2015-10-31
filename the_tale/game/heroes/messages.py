# coding: utf-8
import time
import collections

from the_tale.game.balance import constants as c

from the_tale.game.prototypes import TimePrototype, GameTime

from . import conf

from the_tale.linguistics.lexicon import keys as linguistics_keys



class MessageSurrogate(object):
    __slots__ = ('turn_number', 'timestamp', 'key', 'externals', '_ui_info', '_message', 'restrictions', 'position', '_variables')

    def __init__(self, turn_number, timestamp, key, externals, message, restrictions=frozenset(), position=u'', variables=None):
        self.turn_number = turn_number
        self.timestamp = timestamp
        self.key = key
        self.externals = externals
        self.restrictions = restrictions
        self.position = position

        self._ui_info = None
        self._message = message
        self._variables = variables


    @classmethod
    def create(cls, key, externals, turn_delta=0, restrictions=frozenset(), position=u''):
        return cls(turn_number=TimePrototype.get_current_turn_number()+turn_delta,
                   timestamp=time.time()+turn_delta*c.TURN_DELTA,
                   key=key,
                   externals=externals,
                   message=None,
                   restrictions=restrictions,
                   position=position)

    @classmethod
    def create_fake(cls, key, externals, turn_delta=0, restrictions=frozenset(), position=u''):
        from the_tale.linguistics.logic import fake_text
        return cls(turn_number=TimePrototype.get_current_turn_number()+turn_delta,
                   timestamp=time.time()+turn_delta*c.TURN_DELTA,
                   key=None,
                   externals=externals,
                   message=fake_text(key, externals),
                   restrictions=restrictions,
                   position=position)

    def serialize(self):
        return (self.turn_number, self.timestamp, self.message, self.position, self.key.value if self.key else None, self.get_variables())

    @classmethod
    def deserialize(cls, data):
        return cls(turn_number=data[0],
                   timestamp=data[1],
                   message=data[2],
                   key=linguistics_keys.LEXICON_KEY.index_value.get(data[4]),
                   externals=None,
                   position=data[3],
                   variables=data[5])

    @property
    def message(self):
        from the_tale.linguistics import logic

        if self._message is not None:
            return self._message

        self._message = logic.render_text(lexicon_key=self.key, externals=self.externals, restrictions=self.restrictions)

        return self._message

    def get_variables(self):
        if not self._variables and self.externals:
            self._variables = {name: unicode(external.form) for name, external in self.externals.iteritems()}
        return self._variables

    def ui_info(self, with_info=False):
        if self._ui_info is not None:
            return self._ui_info

        game_time = GameTime.create_from_turn(self.turn_number)

        if with_info:
            self._ui_info = (self.timestamp,
                             game_time.verbose_time,
                             self.message,
                             self.key.value if self.key else None,
                             self.get_variables(),
                             game_time.verbose_date,
                             self.position)
        else:
            self._ui_info = (self.timestamp, game_time.verbose_time, self.message, self.key.value if self.key else None, self.get_variables())

        return self._ui_info

    def clone(self):
        return self.__class__(turn_number=self.turn_number,
                              timestamp=self.timestamp,
                              key=self.key,
                              externals=self.externals,
                              message=self.message, # access .message instead ._message to enshure, that two messages will have one text
                              position=self.position,
                              variables=self.get_variables())


def _message_key(m): return (m.turn_number, m.timestamp)


class MessagesContainer(object):

    __slots__ = ('messages', 'updated')

    MESSAGES_LOG_LENGTH = None

    def __init__(self):
        self.messages = collections.deque(maxlen=self.MESSAGES_LOG_LENGTH)
        self.updated = False

    def push_message(self, msg):
        self.updated = True

        self.messages.append(msg)

        if len(self.messages) > 1 and (self.messages[-1].turn_number < self.messages[-2].turn_number or self.messages[-1].timestamp < self.messages[-2].timestamp):
            moved_message = self.messages[-2]
            self.messages.remove(moved_message)
            self.messages.append(moved_message)

    def messages_number(self):
        return len(self.messages)

    def clear(self):
        if self.messages:
            self.messages.clear()
            self.updated = True

    def __len__(self): return len(self.messages)


    def ui_info(self, with_info=False):
        current_turn = TimePrototype.get_current_turn_number()

        messages = []

        for message in self.messages:
            if message.turn_number > current_turn:
                break

            messages.append(message.ui_info(with_info=with_info))

        return messages

    def serialize(self):
        return {'messages': [message.serialize() for message in self.messages]}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.messages = collections.deque((MessageSurrogate.deserialize(message_data) for message_data in data['messages']),
                                         maxlen=cls.MESSAGES_LOG_LENGTH)
        return obj

    def __eq__(self, other):
        if len(self.messages) != len(other.messages):
            return False

        for a, b in zip(self.messages, other.messages):
            if a.turn_number != b.turn_number or a.message != b.message or abs(a.timestamp - b.timestamp) > 0.0001:
                return False

        return True


class JournalContainer(MessagesContainer):
    MESSAGES_LOG_LENGTH = conf.heroes_settings.MESSAGES_LOG_LENGTH


class DiaryContainer(MessagesContainer):
    MESSAGES_LOG_LENGTH = conf.heroes_settings.DIARY_LOG_LENGTH
