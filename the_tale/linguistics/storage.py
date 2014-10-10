# coding: utf-8
import time

from dext.common.utils import s11n
from dext.settings import settings

from utg import words as utg_words
from utg import templates as utg_templates
from utg import dictionary as utg_dictionary
from utg import lexicon as utg_lexicon

from the_tale.common.utils import storage

from the_tale.linguistics import exceptions
from the_tale.linguistics import prototypes
from the_tale.linguistics import relations


class BaseGameDictionaryStorage(storage.SingleStorage):
    SETTINGS_KEY = None
    EXCEPTION = exceptions.DictionaryStorageError

    def _words_query(self):
        raise NotImplementedError()

    def _construct_zero_item(self):
        return utg_dictionary.Dictionary()

    def refresh(self):
        self.clear()

        for forms in self._words_query():
            word = utg_words.Word.deserialize(s11n.from_json(forms))
            self._item.add_word(word)

        self._version = settings.get(self.SETTINGS_KEY)

    def _get_next_version(self):
        return '%f' % time.time()


class GameDictionaryStorage(BaseGameDictionaryStorage):
    SETTINGS_KEY = 'game dictionary change time'

    def _words_query(self):
        return prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).values_list('forms', flat=True)


class GameLexiconDictionaryStorage(storage.SingleStorage):
    SETTINGS_KEY = 'game lexicon change time'
    EXCEPTION = exceptions.LexiconStorageError

    def _templates_query(self):
        return prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME,
                                                       errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS).values_list('key', 'data')

    def _construct_zero_item(self):
        return utg_lexicon.Lexicon()

    def refresh(self):
        from the_tale.linguistics.lexicon.keys import LEXICON_KEY

        self.clear()

        for key, data in self._templates_query():
            template = utg_templates.Template.deserialize(s11n.from_json(data)['template'])
            self._item.add_template(LEXICON_KEY(key), template)

        self._version = settings.get(self.SETTINGS_KEY)

    def _get_next_version(self):
        return '%f' % time.time()



game_dictionary = GameDictionaryStorage()
game_lexicon = GameLexiconDictionaryStorage()
