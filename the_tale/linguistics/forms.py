# coding: utf-8

from django import forms as django_forms
from dext.forms import forms, fields

from utg import relations as utg_relations
from utg import words as utg_words
from utg import templates as utg_templates
from utg import exceptions as utg_exceptions


from the_tale.linguistics import models
from the_tale.linguistics import prototypes
from the_tale.linguistics.lexicon import logic as lexicon_logic


class BaseWordForm(forms.Form):
    WORD_TYPE = None

    def __init__(self, *args, **kwargs):
        super(BaseWordForm, self).__init__(*args, **kwargs)

        for i, key in enumerate(utg_words.INVERTED_WORDS_CACHES[self.WORD_TYPE]):
            self.fields['field_%d' % i] = fields.CharField(label='', max_length=models.Word.MAX_FORM_LENGTH)

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
        forms = [getattr(self.c, 'field_%d' % i) for i in xrange(len(utg_words.INVERTED_WORDS_CACHES[self.WORD_TYPE]))]

        properties = utg_words.Properties()

        for static_property, required in self.WORD_TYPE.properties.iteritems():
            value = getattr(self.c, 'field_%s' % static_property.__name__)
            if not value:
                continue
            properties.update(value)

        return utg_words.Word(type=self.WORD_TYPE,
                              forms=forms,
                              properties=properties)

    @classmethod
    def get_initials(cls, word):
        initials = {('field_%d' % i): word.forms[i]
                    for i in xrange(len(utg_words.INVERTED_WORDS_CACHES[cls.WORD_TYPE]))}

        for static_property, required in cls.WORD_TYPE.properties.iteritems():
            value = word.properties.is_specified(static_property)
            if not value:
                continue
            initials['field_%s' % static_property.__name__] = value

        return initials


def create_word_type_form(word_type):

    class WordForm(BaseWordForm):
        WORD_TYPE = word_type

    return WordForm


WORD_FORMS = {word_type: create_word_type_form(word_type)
              for word_type in utg_relations.WORD_TYPE.records}


class TemplateForm(forms.Form):
    template = fields.TextField(label=u'шаблон', min_length=1, widget=django_forms.Textarea(attrs={'rows': 3}))

    def __init__(self, key, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.key = key

        verificators = prototypes.Verificator.get_verificators(key=self.key)

        for i, verificator in enumerate(verificators):
            label = u'проверка для %s' % u', '.join(u'%s=%s' % (variable, value) for variable, value in verificator.externals.iteritems())
            self.fields['verificator_%d' % i] = fields.TextField(label=label, required=False, widget=django_forms.Textarea(attrs={'rows': 3}))

    def verificators_fields(self):
        verificators = prototypes.Verificator.get_verificators(key=self.key)
        return [self['verificator_%d' % i] for i, verificator in enumerate(verificators)]

    def verificators(self):

        verificators = prototypes.Verificator.get_verificators(key=self.key)

        for i, verificator in enumerate(verificators):
            verificator.text = getattr(self.c, 'verificator_%d' % i)

        return verificators


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
