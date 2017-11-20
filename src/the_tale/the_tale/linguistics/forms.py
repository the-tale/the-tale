import copy

from django import forms as django_forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

import jinja2

from dext.forms import forms, fields
from dext.common.utils import jinja2 as dext_jinja2
from dext.common.utils import s11n

from utg import relations as utg_relations
from utg import words as utg_words
from utg import data as utg_data
from utg import templates as utg_templates
from utg import exceptions as utg_exceptions


from . import models
from . import storage
from .lexicon import keys as lexicon_keys
from .lexicon.groups import relations as groups_relations


WORD_FIELD_PREFIX = 'word_field'


def get_fields(word_type):
    form_fields = {}

    form_fields.update(get_word_fields_dict(word_type))

    for static_property, required in word_type.properties.items():
        property_type = utg_relations.PROPERTY_TYPE.index_relation[static_property]
        choices = [(r, r.text) for r in static_property.records]
        if not required:
            choices = [('', ' — ')] + choices
        field = fields.TypedChoiceField(label=property_type.text,
                                        choices=choices,
                                        coerce=static_property.get_from_name,
                                        required=False)

        form_fields['%s_%s' % (WORD_FIELD_PREFIX, static_property.__name__)] = field

    return form_fields


def decompress_word(word_type, value):
    if value:
        initials = get_word_fields_initials(value)

        for static_property, required in value.type.properties.items():

            v = value.properties.is_specified(static_property)

            if not v:
                continue

            initials['%s_%s' % (WORD_FIELD_PREFIX, static_property.__name__)] = value.properties.get(static_property)

    else:
        initials = get_fields(word_type)
        initials = {k: '' for k in initials.keys()}

    fields = get_fields(word_type)
    keys = sorted(fields.keys())

    return [initials.get(key) for key in keys]


class WordWidget(django_forms.MultiWidget):

    def __init__(self, word_type, skip_markers=(), show_properties=True, **kwargs):
        fields = get_fields(word_type)
        keys = sorted(fields.keys())

        super(WordWidget, self).__init__(widgets=[fields[key].widget for key in keys],
                                         **kwargs)

        self.word_type = word_type
        self.skip_markers = skip_markers
        self.show_properties = show_properties

    def decompress(self, value):
        return decompress_word(self.word_type, value)

    def format_output(self, rendered_widgets):
        from the_tale.linguistics.word_drawer import FormFieldDrawer

        fields = get_fields(self.word_type)
        keys = {key: i for i, key in enumerate(sorted(fields.keys()))}

        widgets = {key: rendered_widgets[keys[key]] for key in keys}

        drawer = FormFieldDrawer(type=self.word_type, widgets=widgets, skip_markers=self.skip_markers, show_properties=self.show_properties)

        return jinja2.Markup(dext_jinja2.render('linguistics/words/field.html', context={'drawer': drawer}))


@fields.pgf
class WordField(django_forms.MultiValueField):
    LABEL_SUFFIX = ''

    def __init__(self, word_type, show_properties=True, skip_markers=(), **kwargs):
        fields = get_fields(word_type)
        keys = sorted(fields.keys())

        self.fields_keys = dict(enumerate(keys))

        label = kwargs.get('label')
        if label:
            label = mark_safe('<h3>%s</h3>' % label)
            kwargs['label'] = label

        super(WordField, self).__init__(fields=[fields[key] for key in keys],
                                                     widget=WordWidget(word_type=word_type, skip_markers=skip_markers, show_properties=show_properties),
                                                     required=False,
                                                     **kwargs)
        self.word_type = word_type


    def clean(self, value):
        clean_data = []
        errors_count = 0

        if not value or isinstance(value, (list, tuple)):
            if not value or not [v for v in value if v not in self.empty_values]:
                raise ValidationError(self.error_messages['required'], code='required')
        else:
            raise ValidationError(self.error_messages['invalid'], code='invalid')

        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None

            # requered field will be checked in extra errors
            # if self.required and field_value in self.empty_values:
            #     raise ValidationError(self.error_messages['required'], code='required')

            try:
                clean_data.append(field.clean(field_value))
            except ValidationError:
                errors_count += 1

        if errors_count:
            return None

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def compress(self, data_list):
        fields = get_fields(self.word_type)
        keys = {key: i for i, key in enumerate(sorted(fields.keys()))}

        word_forms = [data_list[keys['%s_%d' % (WORD_FIELD_PREFIX, i)]] for i in range(len(utg_data.INVERTED_WORDS_CACHES[self.word_type]))]

        properties = utg_words.Properties()

        for static_property, required in self.word_type.properties.items():
            value = data_list[keys['%s_%s' % (WORD_FIELD_PREFIX, static_property.__name__)]]

            if not value:
                continue

            properties = utg_words.Properties(properties, value)

        word = utg_words.Word(type=self.word_type,
                              forms=word_forms,
                              properties=properties)

        word.autofill_missed_forms()

        return word



def get_word_fields_dict(word_type):
    form_fields = {}

    for i, key in enumerate(utg_data.INVERTED_WORDS_CACHES[word_type]):
        form_fields['%s_%d' % (WORD_FIELD_PREFIX, i)] = fields.CharField(label='', max_length=models.Word.MAX_FORM_LENGTH, required=False)

    return form_fields


def get_word_fields_initials(word):
    return {('%s_%d' % (WORD_FIELD_PREFIX, i)): word.forms[i]
             for i in range(len(utg_data.INVERTED_WORDS_CACHES[word.type]))}


def get_word_forms(form, word_type):
     return [getattr(form.c, '%s_%d' % (WORD_FIELD_PREFIX, i)) for i in range(len(utg_data.INVERTED_WORDS_CACHES[word_type]))]


class BaseWordForm(forms.Form):
    WORD_TYPE = None


def create_word_type_form(word_type):
    class WordForm(BaseWordForm):
        WORD_TYPE = word_type

        word = WordField(word_type=word_type, label=word_type.text[0].upper() + word_type.text[1:])

    return WordForm


WORD_FORMS = {word_type: create_word_type_form(word_type)
              for word_type in utg_relations.WORD_TYPE.records}


class TemplateForm(forms.Form):
    template = fields.TextField(label='Шаблон', min_length=1, widget=django_forms.Textarea(attrs={'rows': 3}))

    def __init__(self, key, verificators, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.key = key
        self.verificators = copy.deepcopy(verificators)

        for i, verificator in enumerate(self.verificators):
            self.fields['verificator_%d' % i] = fields.TextField(label=verificator.get_label(), required=False, widget=django_forms.Textarea(attrs={'rows': 3}))

        for variable in self.key.variables:
            for restrictions_group in variable.type.restrictions:
                field_name = 'restriction_%s_%d' % (variable.value, restrictions_group.value)

                restrictions = storage.restrictions_storage.get_restrictions(restrictions_group)

                restrictions_choices = [(restriction.id, restriction.name) for restriction in restrictions]

                choices = [('', 'нет')]

                if restrictions_group.sort:
                    choices += sorted(restrictions_choices, key=lambda r: r[1])
                else:
                    choices += restrictions_choices

                self.fields[field_name] = fields.ChoiceField(label=restrictions_group.text, required=False, choices=choices)

    def verificators_fields(self):
        return [self['verificator_%d' % i] for i, verificator in enumerate(self.verificators)]

    def variable_restrictions_fields(self, variable):
        x = [self['restriction_%s_%d' % (variable.value, restrictions_group.value)] for restrictions_group in variable.type.restrictions]
        return x

    def clean(self):
        cleaned_data = super(TemplateForm, self).clean()

        for i, verificator in enumerate(self.verificators):
            verificator.text = cleaned_data['verificator_%d' % i]

        return cleaned_data

    def get_restrictions(self):
        restrictions = []

        for variable in self.key.variables:
            for restrictions_group in variable.type.restrictions:
                field_name = 'restriction_%s_%d' % (variable.value, restrictions_group.value)

                restriction_id = self.cleaned_data.get(field_name)

                if not restriction_id:
                    continue

                restrictions.append((variable.value, int(restriction_id)))

        return frozenset(restrictions)

    def clean_template(self):
        data = self.cleaned_data['template'].strip()

        # TODO: test exceptions
        try:
            template = utg_templates.Template()
            template.parse(data, externals=[v.value for v in self.key.variables])
        except utg_exceptions.WrongDependencyFormatError as e:
            raise django_forms.ValidationError('Ошибка в формате подстановки: %s' % e.arguments['dependency'])
        except utg_exceptions.UnknownVerboseIdError as e:
            raise django_forms.ValidationError('Неизвестная форма слова: %s' % e.arguments['verbose_id'])
        except utg_exceptions.ExternalDependecyNotFoundError as e:
            raise django_forms.ValidationError('Неизвестная переменная: %s' % e.arguments['dependency'])

        return data

    @classmethod
    def get_initials(cls, template, verificators):
        initials = {'template': template.raw_template}

        for i, verificator in enumerate(verificators):
            initials['verificator_%d' % i] = verificator.text

        for variable, restrictions in template.restrictions.items():
            for restriction in restrictions:
                field_name = 'restriction_%s_%d' % (variable.value, restriction.group.value)
                initials[field_name] = restriction.id

        return initials


KEY_CHOICES = []

for group in groups_relations.LEXICON_GROUP.records:
    keys = []
    for key in lexicon_keys.LEXICON_KEY.records:
        if key.group != group:
            continue
        keys.append((key, key.text))
    keys.sort(key=lambda x: x[1])
    KEY_CHOICES.append((group.text, keys))


class TemplateKeyForm(forms.Form):
    key = django_forms.TypedChoiceField(label='Тип фразы', choices=KEY_CHOICES, coerce=lexicon_keys.LEXICON_KEY.get_from_name)


class LoadDictionaryForm(forms.Form):
    words = fields.TextField(label='Данные словаря')

    def clean_words(self):
        data = self.cleaned_data.get('words')

        if data is None:
            raise ValidationError('Нет данных', code='not_json')

        try:
            words_data = s11n.from_json(data)
        except ValueError:
            raise ValidationError('Данные должны быть в формате JSON', code='not_json')

        try:
            words = [utg_words.Word.deserialize(word_data) for word_data in words_data.get('words')]
        except:
            raise ValidationError('Неверный формат описания слов', code='wrong_words_format')

        return words
