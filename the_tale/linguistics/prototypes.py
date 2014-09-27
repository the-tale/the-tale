# coding: utf-8
import random
import datetime

from dext.common.utils import s11n

from utg import words as utg_words
from utg import templates as utg_templates

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.linguistics import models
from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import logic as lexicon_logic
from the_tale.linguistics.lexicon import dictionary as lexicon_dictionary


class WordPrototype(BasePrototype):
    _model_class = models.Word
    _readonly = ('id', 'type', 'created_at', 'parent_id')
    _bidirectional = ('state', )
    _get_by = ('id', 'parent_id')

    @lazy_property
    def utg_word(self):
        return utg_words.Word.deserialize(s11n.from_json(self._model.forms))

    def get_parent(self):
        if self.parent_id is None:
            return None
        return WordPrototype.get_by_id(self.parent_id)

    def get_child(self):
        return self.get_by_parent_id(self.id)

    def has_parent(self): return bool(self.get_parent())
    def has_child(self): return bool(self.get_child())


    @classmethod
    def create(cls, utg_word, parent=None):
        from the_tale.linguistics import storage

        model = cls._db_create(type=utg_word.type,
                               state=relations.WORD_STATE.ON_REVIEW,
                               normal_form=utg_word.normal_form(),
                               forms=s11n.to_json(utg_word.serialize()),
                               parent=parent._model if parent is not None else None)

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
    _readonly = ('id', 'key', 'created_at', 'raw_template', 'author_id')
    _bidirectional = ('state', 'parent_id')
    _get_by = ('id',)

    @lazy_property
    def _data(self):
        return s11n.from_json(self._model.data)

    @lazy_property
    def lexicon_groups(self):
        return {key: tuple(value) for key, value in self._data['groups'].iteritems()}

    @lazy_property
    def verificators(self):
        return [Verificator.deserialize(v) for v in self._data['verificators']]

    @lazy_property
    def utg_template(self):
        return utg_templates.Template.deserialize(self._data['template'])

    @classmethod
    def get_start_verificatos(self, key):
        groups = lexicon_logic.get_verificators_groups(key=key, old_groups=())
        verificators = Verificator.get_verificators(key=key, groups=groups, old_verificators=())
        return verificators

    def get_all_verificatos(self):
        groups = lexicon_logic.get_verificators_groups(key=self.key, old_groups=self.lexicon_groups)
        verificators = Verificator.get_verificators(key=self.key, groups=groups, old_verificators=self.verificators)
        return verificators

    def get_errors(self, utg_dictionary):
        from utg.data import VERBOSE_TO_PROPERTIES

        errors = []

        verificators = self.get_all_verificatos()

        unexisted_words = self.utg_template.get_undictionaried_words(externals=[v.value for v in self.key.variables],
                                                                     dictionary=utg_dictionary)

        for word in unexisted_words:
            errors.append(u'Неизвестное слово: «%s»' % word)

        if errors:
            return errors

        for verificator in verificators:
            externals = {}
            for k, (word_form, additional_properties) in verificator.externals.iteritems():
                word_form = lexicon_dictionary.DICTIONARY.get_word(word_form)
                if additional_properties:
                    word_form.properties.update(*[VERBOSE_TO_PROPERTIES[prop.strip()] for prop in additional_properties.split(',') if prop])

                externals[k] = word_form

            template_render = self.utg_template.substitute(externals=externals, dictionary=utg_dictionary)

            if verificator.text != template_render:
                errors.append(u'Проверочный текст не совпадает с интерпретацией шаблона [%s]' % template_render)

        return errors


    @classmethod
    def create(cls, key, raw_template, utg_template, verificators, author, parent=None):
        model = cls._db_create(key=key,
                               state=relations.TEMPLATE_STATE.ON_REVIEW,
                               raw_template=raw_template,
                               author=None if author is None else author._model,
                               parent=None if parent is None else parent._model,
                               data=s11n.to_json({'verificators': [v.serialize() for v in verificators],
                                                  'template': utg_template.serialize(),
                                                  'groups': lexicon_logic.get_verificators_groups(key=key)}))

        return cls(model)


    def update(self, raw_template, utg_template, verificators):
        self._model.raw_template = raw_template
        self._model.data = s11n.to_json({'verificators': [v.serialize() for v in verificators],
                                         'template': utg_template.serialize()})

        del self._data
        del self.verificators
        del self.utg_template
        del self.lexicon_groups

        self.save()


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
        return cls(text=data['text'],
                   externals={k: tuple(v) for k,v in data['externals'].iteritems()})

    def __eq__(self, other):
        return (self.text == other.text and
                self.externals == other.externals)


    @classmethod
    def get_verificators(cls, key, groups, old_verificators=()):
        from the_tale.linguistics.lexicon.relations import VARIABLE_VERIFICATOR

        random_state = random.getstate()
        random.seed(key.value)

        start_substitutions = {}
        used_substitutions = {}
        work_substitutions = {}

        for variable_value, (verificator_value, substitution_index) in groups.iteritems():
            verificator = VARIABLE_VERIFICATOR(verificator_value)
            start_substitutions[variable_value] = set(verificator.substitutions[substitution_index])
            work_substitutions[variable_value] = set(start_substitutions[variable_value])
            used_substitutions[variable_value] = set()

        verificators = []

        for old_verificator in old_verificators:
            correct_verificator = True

            for variable_value, substitution in old_verificator.externals.iteritems():
                if substitution not in work_substitutions[variable_value]:
                    correct_verificator = False
                    break

            if not correct_verificator:
                continue

            verificators.append(old_verificator)

            for variable_value, substitution in old_verificator.externals.iteritems():
                used_substitutions[variable_value].add(substitution)

                work_substitution = work_substitutions[variable_value]
                work_substitution.remove(substitution)
                if not work_substitution:
                    work_substitution |= start_substitutions[variable_value]

        while used_substitutions != start_substitutions:
            externals = {}

            for variable_value, substitutions in work_substitutions.iteritems():
                substitution = random.choice(list(substitutions))

                used_substitutions[variable_value].add(substitution)

                externals[variable_value] = substitution

                substitutions.remove(substitution)

                if not substitutions:
                    substitutions |= start_substitutions[variable_value]

            verificators.append(cls(text=u'', externals=externals))

        random.setstate(random_state)

        return verificators
