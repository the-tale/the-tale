# coding: utf-8
import time

from dext.common.utils import s11n
from dext.settings import settings
from dext.common.utils import storage as dext_storage

from utg import words as utg_words
from utg import templates as utg_templates
from utg import dictionary as utg_dictionary
from utg import lexicon as utg_lexicon

from the_tale.common.utils import storage

from the_tale.linguistics import exceptions
from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import objects
from the_tale.linguistics import models


class BaseGameDictionaryStorage(storage.SingleStorage):
    SETTINGS_KEY = None
    EXCEPTION = exceptions.DictionaryStorageError

    def _words_query(self):
        raise NotImplementedError()

    def _construct_zero_item(self):
        return utg_dictionary.Dictionary()

    def refresh(self):
        self.clear()

        for forms in self._words_query().iterator():
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

        for key, data in self._templates_query().iterator():
            data = s11n.from_json(data)
            template = utg_templates.Template.deserialize(data['template'])
            restrictions = frozenset(tuple(key) for key in data.get('restrictions', ()))
            self._item.add_template(LEXICON_KEY(key), template, restrictions=restrictions)

        self._version = settings.get(self.SETTINGS_KEY)

    def _get_next_version(self):
        return '%f' % time.time()



game_dictionary = GameDictionaryStorage()
game_lexicon = GameLexiconDictionaryStorage()



class RestrictionsStorage(dext_storage.Storage):
    SETTINGS_KEY = 'linguisitcs-restrictions-storage'
    EXCEPTION = exceptions.RestrictionsStorageError

    def _construct_object(self, model):
        return objects.Restriction.from_model(model)

    def _get_all_query(self):
        return models.Restriction.objects.all()

    def clear(self):
        super(RestrictionsStorage, self).clear()
        self._restrictions = {}
        self._restrictions_by_group = {}

    def add_item(self, id_, item):
        super(RestrictionsStorage, self).add_item(id_, item)
        self._restrictions[item.storage_key()] = item

        if item.group not in self._restrictions_by_group:
            self._restrictions_by_group[item.group] = []

        self._restrictions_by_group[item.group].append(item)

    def get_restriction(self, group, external_id):
        self.sync()
        return self._restrictions.get((group.value, external_id))

    def get_restrictions(self, group):
        self.sync()
        return self._restrictions_by_group.get(group, ())

    def get_form_choices(self):
        choices = [(None, u'нет')]

        for restriction_group in relations.TEMPLATE_RESTRICTION_GROUP.records:
            restrictions = [(r.id, r.name) for r in sorted(self.get_restrictions(restriction_group), key=lambda r: r.name)]
            choices.append((restriction_group.text, restrictions))


        return choices


restrictions_storage = RestrictionsStorage()
