# coding: utf-8
import random
import datetime

from dext.common.utils import s11n

from utg import words as utg_words
from utg import templates as utg_templates
from utg import exceptions as utg_exceptions
from utg.data import VERBOSE_TO_PROPERTIES

from the_tale.amqp_environment import environment

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.linguistics import models
from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import logic as lexicon_logic
from the_tale.linguistics.lexicon import dictionary as lexicon_dictionary


class WordPrototype(BasePrototype):
    _model_class = models.Word
    _readonly = ('id', 'type', 'created_at')
    _bidirectional = ('state', 'parent_id', 'used_in_ingame_templates', 'used_in_onreview_templates', 'used_in_status')
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
        model = cls._db_create(type=utg_word.type,
                               state=relations.WORD_STATE.ON_REVIEW,
                               normal_form=utg_word.normal_form(),
                               forms=s11n.to_json(utg_word.serialize()),
                               parent=parent._model if parent is not None else None)

        prototype = cls(model)

        environment.workers.linguistics_manager.cmd_game_dictionary_changed()

        return prototype

    def save(self):
        from the_tale.linguistics import storage

        self._model.forms = s11n.to_json(self.utg_word.serialize())
        self._model.normal_form = self.utg_word.normal_form()
        self._model.updated_at = datetime.datetime.now()

        super(WordPrototype, self).save()

        if self.state.is_IN_GAME:
            storage.game_dictionary.update_version()
            storage.game_dictionary.refresh()

        environment.workers.linguistics_manager.cmd_game_dictionary_changed()


    def remove(self):
        self._model.delete()

    def update_used_in_status(self, used_in_ingame_templates, used_in_onreview_templates, force_update=True):
        changed = (self.used_in_ingame_templates != used_in_ingame_templates or self.used_in_onreview_templates != used_in_onreview_templates)

        self.used_in_ingame_templates = used_in_ingame_templates
        self.used_in_onreview_templates = used_in_onreview_templates

        if self.used_in_ingame_templates > 0:
            self.used_in_status = relations.WORD_USED_IN_STATUS.IN_INGAME_TEMPLATES
        elif self.used_in_onreview_templates > 0:
            self.used_in_status = relations.WORD_USED_IN_STATUS.IN_ONREVIEW_TEMPLATES
        else:
            self.used_in_status = relations.WORD_USED_IN_STATUS.NOT_USED

        if force_update and changed:
            self._db_filter(id=self.id).update(used_in_status=self.used_in_status,
                                               used_in_ingame_templates=self.used_in_ingame_templates,
                                               used_in_onreview_templates=self.used_in_onreview_templates)



class TemplatePrototype(BasePrototype):
    _model_class = models.Template
    _readonly = ('id', 'key', 'created_at', 'raw_template', 'author_id')
    _bidirectional = ('state', 'parent_id', 'errors_status')
    _get_by = ('id', 'parent_id')

    def get_parent(self):
        if self.parent_id is None:
            return None
        return TemplatePrototype.get_by_id(self.parent_id)

    def get_child(self):
        return self.get_by_parent_id(self.id)


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

    def get_errors(self):
        from the_tale.linguistics import storage

        utg_dictionary = storage.game_dictionary.item

        errors = []

        verificators = self.get_all_verificatos()

        unexisted_words = self.utg_template.get_undictionaried_words(externals=[v.value for v in self.key.variables],
                                                                     dictionary=utg_dictionary)

        for word in unexisted_words:
            errors.append(u'Неизвестное слово: «%s»' % word)

        if errors:
            return errors

        for verificator in verificators:
            externals = verificator.preprocessed_externals()

            try:
                template_render = self.utg_template.substitute(externals=externals, dictionary=utg_dictionary)
            except utg_exceptions.MoreThenOneWordFoundError as e:
                errors.append(u'Невозможно однозначно определить слово с формой «%s» — существует несколько слов с такими формами. Укажите более точные свойства.' %
                              e.arguments['text'])
                return errors

            if verificator.text != template_render:
                errors.append(u'Проверочный текст не совпадает с интерпретацией шаблона [%s]' % template_render)

        return errors

    def has_errors(self):
        return bool(self.get_errors())


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
        prototype = cls(model)

        prototype.update_errors_status(force_update=True)

        environment.workers.linguistics_manager.cmd_game_lexicon_changed()

        return prototype


    def update(self, raw_template=None, utg_template=None, verificators=None):
        if raw_template is not None:
            self._model.raw_template = raw_template

        self.del_lazy_properties()

        if verificators is not None:
            self._data['verificators'] = [v.serialize() for v in verificators]

        if utg_template is not None:
            self._data['template'] = utg_template.serialize()

        self._data['groups'] = self.lexicon_groups

        self.save()


    def save(self):
        from the_tale.linguistics import storage

        self._data['verificators'] = [v.serialize() for v in self.verificators]
        self._data['template'] = self.utg_template.serialize()
        self._data['groups'] = self.lexicon_groups

        self._model.data = s11n.to_json(self._data)

        self._model.updated_at = datetime.datetime.now()

        self.update_errors_status(force_update=False)

        super(TemplatePrototype, self).save()

        if self.state.is_IN_GAME:
            storage.game_lexicon.update_version()
            storage.game_lexicon.refresh()

        environment.workers.linguistics_manager.cmd_game_lexicon_changed()

    def remove(self):
        self._model.delete()

    def update_errors_status(self, force_update=False):
        old_errors_status = self.errors_status

        if self.has_errors():
            self.errors_status = relations.TEMPLATE_ERRORS_STATUS.HAS_ERRORS
        else:
            self.errors_status = relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS

        if force_update and old_errors_status != self.errors_status:
            self._db_filter(id=self.id).update(errors_status=self.errors_status)

        return old_errors_status != self.errors_status


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

    def get_label(self):
        externals = self.preprocessed_externals()
        return u'Проверка для %s' % u', '.join(u'%s=%s' % (variable, value.form) for variable, value in externals.iteritems())

    def preprocessed_externals(self):
        externals = {}
        for k, (word_form, additional_properties) in self.externals.iteritems():
            word_form = lexicon_dictionary.DICTIONARY.get_word(word_form)
            if additional_properties:
                properties = utg_words.Properties(word_form.properties,
                                                *[VERBOSE_TO_PROPERTIES[prop.strip()] for prop in additional_properties.split(',') if prop])
                word_form = utg_words.WordForm(word=word_form.word,
                                               properties=properties)

            externals[k] = word_form

        return externals

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
