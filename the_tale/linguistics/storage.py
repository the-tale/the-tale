# coding: utf-8
import time

from dext.common.utils import s11n
from dext.settings import settings

from utg import words as utg_words
from utg import dictionary as utg_dictionary

from the_tale.common.utils import storage

from the_tale.linguistics import exceptions
from the_tale.linguistics import prototypes
from the_tale.linguistics import relations


class BaseGameDictionaryStorage(storage.SingleStorage):
    SETTINGS_KEY = None
    EXCEPTION = exceptions.DictionaryStorageError

    def _words_query(self):
        raise NotImplementedError()

    def refresh(self):
        self.clear()

        self._item = utg_dictionary.Dictionary()

        for forms in self._words_query():
            word = utg_words.Word.deserialize(s11n.from_json(forms))
            self._item.add_word(word)

        self._version = settings[self.SETTINGS_KEY]

    def _get_next_version(self):
        return '%f' % time.time()


class GameDictionaryStorage(BaseGameDictionaryStorage):
    SETTINGS_KEY = 'game dictionary change time'

    def _words_query(self):
        return prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).values_list('forms', flat=True)


class RawDictionaryStorage(BaseGameDictionaryStorage):
    SETTINGS_KEY = 'raw dictionary change time'

    def _words_query(self):
        words = {}

        for forms, normal_form, type, state in  prototypes.WordPrototype._db_all().values_list('forms', 'normal_form', 'type', 'state'):
            if relations.WORD_STATE(state).is_IN_GAME and (type, normal_form) in words:
                continue
            words[(type, normal_form)] = forms

        return words.itervalues()


game_dictionary = GameDictionaryStorage()
raw_dictionary = RawDictionaryStorage()
