# coding: utf-8
import datetime

from dext.common.utils import s11n

from utg import words as utg_words
from utg import templates as utg_templates

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.linguistics import models
from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import logic as lexicon_logic


class WordPrototype(BasePrototype):
    _model_class = models.Word
    _readonly = ('id', 'type', 'created_at')
    _bidirectional = ('state', )
    _get_by = ('id',)

    @lazy_property
    def utg_word(self):
        return utg_words.Word.deserialize(s11n.from_json(self._model.forms))

    def has_on_review_copy(self):
        if self.state.is_ON_REVIEW:
            return False

        return self._db_filter(state=relations.WORD_STATE.ON_REVIEW, normal_form=self.utg_word.normal_form(), type=self.type).exists()

    @classmethod
    def create(cls, utg_word):
        from the_tale.linguistics import storage

        model = cls._db_create(type=utg_word.type,
                               state=relations.WORD_STATE.ON_REVIEW,
                               normal_form=utg_word.normal_form(),
                               forms=s11n.to_json(utg_word.serialize()))

        prototype = cls(model)

        storage.raw_dictionary.update_version()
        storage.raw_dictionary.refresh()

        return prototype

    def save(self):
        from the_tale.linguistics import storage

        self._model.forms = s11n.to_json(self.utg_word.serialize())
        self._model.normal_form = self.utg_word.normal_form()
        self._model.updated_at = datetime.datetime.now()

        super(WordPrototype, self).save()

        storage.raw_dictionary.update_version()
        storage.raw_dictionary.refresh()

        if self.state.is_IN_GAME:
            storage.game_dictionary.update_version()
            storage.game_dictionary.refresh()


    def remove(self):
        self._model.delete()



class TemplatePrototype(BasePrototype):
    _model_class = models.Template
    _readonly = ('id', 'key', 'created_at', 'raw_template')
    _bidirectional = ('state',)
    _get_by = ('id',)

    @lazy_property
    def _data(self):
        return s11n.from_json(self._model.data)

    @lazy_property
    def verificators(self):
        return [Verificator.deserialize(v) for v in self._data['verificators']]

    @lazy_property
    def utg_template(self):
        return utg_templates.Template.deserialize(self._data['template'])

    def get_errors(self, utg_dictionary):

        errors = []

        verificators = Verificator.get_verificators(key=self.key, old_verificators=self.verificators)

        unexisted_words = self.utg_template.get_undictionaried_words(externals=[v.value for v in self.key.variables],
                                                                     dictionary=utg_dictionary)

        for word in unexisted_words:
            errors.append(u'Неизвестное слово: «%s»' % word)

        if errors:
            return errors

        for verificator in verificators:
            externals = {k: utg_dictionary.get_word(v) for k, v in verificator.externals.iteritems()}
            template_render = self.utg_template.substitute(externals=externals, dictionary=utg_dictionary)

            if verificator.text != template_render:
                errors.append(u'Проверочный текст не совпадает с интерпретацией шаблона [%s]' % template_render)

        return errors


    @classmethod
    def create(cls, key, raw_template, utg_template, verificators):
        model = cls._db_create(key=key,
                               state=relations.TEMPLATE_STATE.ON_REVIEW,
                               raw_template=raw_template,
                               data=s11n.to_json({'verificators': [v.serialize() for v in verificators],
                                                  'template': utg_template.serialize()}))

        return cls(model)

    def save(self):
        self._model.template = s11n.to_json(self.utg_template.serialize())
        self._model.data = s11n.to_json(self._data)
        self._model.updated_at = datetime.datetime.now()
        super(TemplatePrototype, self).save()

    def remove(self):
        self._model.delete()



class Verificator(object):
    __slots__ = ('text', 'externals')

    def __init__(self, text, externals):
        self.text = text
        self.externals = externals

    def serialize(self):
        return {'text': self.text,
                'externals': self.externals}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    def __eq__(self, other):
        return (self.text == other.text,
                self.externals == other.externals)

    @classmethod
    def get_verificators(cls, key, old_verificators=()):
        externals = lexicon_logic.get_verificators_externals(key)

        valid_verificators = [verificator for verificator in old_verificators if any(e == verificator.externals for e in externals)]

        new_externals = [e for e in externals if all(e != verificator.externals for verificator in valid_verificators)]

        return valid_verificators + [cls(text=u'', externals=e) for e in new_externals]
