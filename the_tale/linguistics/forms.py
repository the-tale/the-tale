# coding: utf-8

from django import forms as django_forms
from dext.forms import forms, fields

from utg import relations as utg_relations
from utg import words as utg_words
from utg import templates as utg_templates


from the_tale.linguistics import models
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

        verificators_externals = lexicon_logic.get_verificators_externals(self.key)

        for i, externals in enumerate(verificators_externals):
            label = u'проверка для %s' % u', '.join(u'%s=%s' % (variable, value) for variable, value in externals.iteritems())
            self.fields['verificator_%d' % i] = fields.TextField(label=label, required=False, widget=django_forms.Textarea(attrs={'rows': 3}))

    def verificators_fields(self):
        verificators_externals = lexicon_logic.get_verificators_externals(self.key)
        return [self['verificator_%d' % i] for i, externals in enumerate(verificators_externals)]

    def verificators(self):
        from the_tale.linguistics import prototypes

        verificators_externals = lexicon_logic.get_verificators_externals(self.key)

        verificators = []

        for i, externals in enumerate(verificators_externals):
            verificator_id = 'verificator_%d' % i
            verificator_text = getattr(self.c, verificator_id)
            verificators.append(prototypes.Verificator(text=verificator_text, externals=dict(externals)))

        return verificators


    def clean_template(self):
        data = self.cleaned_data['template']

        template = utg_templates.Template()

        template.parse(data, externals=[v.value for v in self.key.variables])

        return template
