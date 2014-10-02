# coding: utf-8

from django import forms as django_forms
from dext.forms import forms, fields

from utg import relations as utg_relations
from utg import words as utg_words
from utg import data as utg_data
from utg import templates as utg_templates
from utg import exceptions as utg_exceptions


from the_tale.linguistics import models


def get_word_fields_dict(word_type):
    form_fields = {}

    for i, key in enumerate(utg_data.INVERTED_WORDS_CACHES[word_type]):
        form_fields['field_%d' % i] = fields.CharField(label='', max_length=models.Word.MAX_FORM_LENGTH)

    return form_fields


def get_word_fields_initials(word):
     return {('field_%d' % i): word.forms[i]
             for i in xrange(len(utg_data.INVERTED_WORDS_CACHES[word.type]))}


def get_word_forms(form, word_type):
     return [getattr(form.c, 'field_%d' % i) for i in xrange(len(utg_data.INVERTED_WORDS_CACHES[word_type]))]


class BaseWordForm(forms.Form):
    WORD_TYPE = None

    def __init__(self, *args, **kwargs):
        super(BaseWordForm, self).__init__(*args, **kwargs)

        self.fields.update(get_word_fields_dict(self.WORD_TYPE))

        for patch in self.WORD_TYPE.patches:
            for i, key in enumerate(utg_data.INVERTED_WORDS_CACHES[patch]):
                self.fields['patch_field_%d_%d' % (patch.value, i)] = fields.CharField(label='', max_length=models.Word.MAX_FORM_LENGTH, required=False)

        for static_property, required in self.WORD_TYPE.properties.iteritems():
            property_type = utg_relations.PROPERTY_TYPE.index_relation[static_property]
            choices = [(r, r.text) for r in static_property.records]
            if not required:
                choices = [('', u' — ')] + choices
            field = fields.TypedChoiceField(label=property_type.text,
                                            choices=choices,
                                            coerce=static_property.get_from_name,
                                            required=False)
            self.fields['field_%s' % static_property.__name__] = field

    def get_word(self):
        forms = get_word_forms(form=self, word_type=self.WORD_TYPE)

        patches = {}

        for patch in self.WORD_TYPE.patches:
            patch_forms = [getattr(self.c, 'patch_field_%d_%d' % (patch.value, i)) for i in xrange(len(utg_data.INVERTED_WORDS_CACHES[patch]))]

            if not all(form for form in patch_forms):
                continue

            patches[patch] = utg_words.Word(type=patch,
                                            forms=patch_forms,
                                            properties=utg_words.Properties())

        properties = utg_words.Properties()

        for static_property, required in self.WORD_TYPE.properties.iteritems():
            value = getattr(self.c, 'field_%s' % static_property.__name__)
            if not value:
                continue
            properties = utg_words.Properties(properties, value)

        return utg_words.Word(type=self.WORD_TYPE,
                              forms=forms,
                              properties=properties,
                              patches=patches)

    @classmethod
    def get_initials(cls, word):
        initials = get_word_fields_initials(word)

        for patch in word.type.patches:
            for i, key in enumerate(utg_data.INVERTED_WORDS_CACHES[patch]):
                initials['patch_field_%d_%d' % (patch.value, i)] = word.patches[patch].forms[i] if patch in word.patches else u''


        for static_property, required in cls.WORD_TYPE.properties.iteritems():
            value = word.properties.is_specified(static_property)
            if not value:
                continue
            initials['field_%s' % static_property.__name__] = word.properties.get(static_property)

        return initials


def create_word_type_form(word_type):

    class WordForm(BaseWordForm):
        WORD_TYPE = word_type

    return WordForm


WORD_FORMS = {word_type: create_word_type_form(word_type)
              for word_type in utg_relations.WORD_TYPE.records}


class TemplateForm(forms.Form):
    template = fields.TextField(label=u'шаблон', min_length=1, widget=django_forms.Textarea(attrs={'rows': 3}))

    def __init__(self, key, verificators, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.key = key
        self.verificators = verificators

        for i, verificator in enumerate(self.verificators):
            self.fields['verificator_%d' % i] = fields.TextField(label=verificator.get_label(), required=False, widget=django_forms.Textarea(attrs={'rows': 3}))

    def verificators_fields(self):
        return [self['verificator_%d' % i] for i, verificator in enumerate(self.verificators)]

    def clean(self):
        cleaned_data = super(TemplateForm, self).clean()

        for i, verificator in enumerate(self.verificators):
            verificator.text = cleaned_data['verificator_%d' % i]

        return cleaned_data


    def clean_template(self):
        data = self.cleaned_data['template'].strip()

        # TODO: test exceptions
        try:
            template = utg_templates.Template()
            template.parse(data, externals=[v.value for v in self.key.variables])
        except utg_exceptions.WrongDependencyFormatError, e:
            raise django_forms.ValidationError(u'Ошибка в формате подстановки: %s' % e.arguments['dependency'])
        except utg_exceptions.UnknownVerboseIdError, e:
            raise django_forms.ValidationError(u'Неизвестная форма слова: %s' % e.arguments['verbose_id'])
        except utg_exceptions.ExternalDependecyNotFoundError, e:
            raise django_forms.ValidationError(u'Неизвестная переменная: %s' % e.arguments['dependency'])

        return data

    @classmethod
    def get_initials(cls, template, verificators):
        initials = {'template': template.raw_template}

        for i, verificator in enumerate(verificators):
            initials['verificator_%d' % i] = verificator.text

        return initials
