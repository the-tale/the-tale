
import smart_imports

smart_imports.all()


WORD_FIELD_PREFIX = 'word_field'


def get_fields(word_type):
    form_fields = {}

    form_fields.update(get_word_fields_dict(word_type))

    for static_property, required in word_type.properties.items():
        property_type = utg_relations.PROPERTY_TYPE.index_relation[static_property]
        choices = [(r, r.text) for r in static_property.records]
        if not required:
            choices = [('', ' — ')] + choices
        field = dext_fields.TypedChoiceField(label=property_type.text,
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
        fields = get_fields(self.word_type)
        keys = {key: i for i, key in enumerate(sorted(fields.keys()))}

        widgets = {key: rendered_widgets[keys[key]] for key in keys}

        drawer = word_drawer.FormFieldDrawer(type=self.word_type, widgets=widgets, skip_markers=self.skip_markers, show_properties=self.show_properties)

        return jinja2.Markup(dext_jinja2.render('linguistics/words/field.html', context={'drawer': drawer}))


class SimpleNounWidget(WordWidget):

    def format_output(self, rendered_widgets):
        fields = get_fields(self.word_type)
        keys = {key: i for i, key in enumerate(sorted(fields.keys()))}

        leaf = word_drawer.Leaf(type=self.word_type,
                                base=relations.WORD_BLOCK_BASE.C,
                                key={utg_relations.NUMBER: utg_relations.NUMBER.SINGULAR,
                                     utg_relations.NOUN_FORM: utg_relations.NOUN_FORM.NORMAL})

        widgets = {key: rendered_widgets[keys[key]] for key in keys}

        drawer = word_drawer.FormFieldDrawer(type=self.word_type, widgets=widgets, skip_markers=self.skip_markers, show_properties=self.show_properties)
        return jinja2.Markup(dext_jinja2.render('linguistics/words/simple_noun_field.html', context={'drawer': drawer,
                                                                                                     'leaf': leaf}))


@dext_fields.pgf
class WordField(django_forms.MultiValueField):
    LABEL_SUFFIX = ''

    def __init__(self, word_type, show_properties=True, skip_markers=(), min_length=1, widget_class=WordWidget, **kwargs):
        fields = get_fields(word_type)
        keys = sorted(fields.keys())

        self.fields_keys = dict(enumerate(keys))

        label = kwargs.get('label')
        if label:
            label = django_safestring.mark_safe('<h3>%s</h3>' % label)
            kwargs['label'] = label

        super(WordField, self).__init__(fields=[fields[key] for key in keys],
                                        widget=widget_class(word_type=word_type,
                                                            skip_markers=skip_markers,
                                                            show_properties=show_properties),
                                        required=False,
                                        **kwargs)
        self.word_type = word_type
        self.min_length = min_length

    def clean(self, value):
        clean_data = []
        errors_count = 0

        if not value or isinstance(value, (list, tuple)):
            if not value or not [v for v in value if v not in self.empty_values]:
                raise django_forms.ValidationError(self.error_messages['required'], code='required')
        else:
            raise django_forms.ValidationError(self.error_messages['invalid'], code='invalid')

        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None

            # requered field will be checked in extra errors
            # if self.required and field_value in self.empty_values:
            #     raise django_forms.ValidationError(self.error_messages['required'], code='required')

            try:
                clean_data.append(field.clean(field_value))
            except django_forms.ValidationError:
                errors_count += 1

        if errors_count:
            return None

        word = self.compress(clean_data)

        for form in word.forms:
            if len(form) < self.min_length:
                raise django_forms.ValidationError('Минимальная длинна каждой формы слова должна быть не меньше {}'.format(self.min_length), code='min_length')

        self.validate(word)
        self.run_validators(word)
        return word

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
        form_fields['%s_%d' % (WORD_FIELD_PREFIX, i)] = dext_fields.CharField(label='',
                                                                              max_length=models.Word.MAX_FORM_LENGTH,
                                                                              required=False)

    return form_fields


def get_word_fields_initials(word):
    return {('%s_%d' % (WORD_FIELD_PREFIX, i)): word.forms[i]
            for i in range(len(utg_data.INVERTED_WORDS_CACHES[word.type]))}


def get_word_forms(form, word_type):
    return [getattr(form.c, '%s_%d' % (WORD_FIELD_PREFIX, i)) for i in range(len(utg_data.INVERTED_WORDS_CACHES[word_type]))]


class BaseWordForm(dext_forms.Form):
    WORD_TYPE = None


def create_word_type_form(word_type):
    class WordForm(BaseWordForm):
        WORD_TYPE = word_type

        word = WordField(word_type=word_type, label=word_type.text[0].upper() + word_type.text[1:])

    return WordForm


WORD_FORMS = {word_type: create_word_type_form(word_type)
              for word_type in utg_relations.WORD_TYPE.records}


class TemplateForm(dext_forms.Form):
    template = dext_fields.TextField(label='Шаблон', min_length=1, widget=django_forms.Textarea(attrs={'rows': 3}))

    def __init__(self, key, verificators, *args, **kwargs):
        self.template_id = kwargs.pop('template_id', None)

        super(TemplateForm, self).__init__(*args, **kwargs)
        self.key = key
        self.verificators = copy.deepcopy(verificators)

        for i, verificator in enumerate(self.verificators):
            self.fields['verificator_%d' % i] = dext_fields.TextField(label=verificator.get_label(), required=False, widget=django_forms.Textarea(attrs={'rows': 3}))

        for variable in self.key.variables:
            for restrictions_group in variable.type.restrictions:
                field_name = 'restriction_%s_%d' % (variable.value, restrictions_group.value)

                restrictions = storage.restrictions.get_restrictions(restrictions_group)

                restrictions_choices = [(restriction.id, restriction.name) for restriction in restrictions]

                choices = [('', 'нет')]

                if restrictions_group.sort:
                    choices += sorted(restrictions_choices, key=lambda r: r[1])
                else:
                    choices += restrictions_choices

                self.fields[field_name] = dext_fields.ChoiceField(label=restrictions_group.text, required=False, choices=choices)

    def verificators_fields(self):
        return [self['verificator_%d' % i] for i, verificator in enumerate(self.verificators)]

    def variable_restrictions_fields(self, variable):
        x = [self['restriction_%s_%d' % (variable.value, restrictions_group.value)] for restrictions_group in variable.type.restrictions]
        return x

    def clean(self):
        cleaned_data = super(TemplateForm, self).clean()

        for i, verificator in enumerate(self.verificators):
            verificator.text = cleaned_data['verificator_%d' % i]

        if self.key.group.is_HERO_HISTORY:
            self.check_hero_history_restrictions()

        return cleaned_data

    def check_hero_history_restrictions(self):
        current_restrictions = self.get_restrictions()

        allowed_reistrictions = {
            lexicon_relations.VARIABLE.HERO.value: {
                restrictions.GROUP.GENDER: [record.value for record in game_relations.GENDER.records],
                restrictions.GROUP.RACE: [record.value for record in game_relations.RACE.records],
                restrictions.GROUP.HABIT_HONOR: [game_relations.HABIT_HONOR_INTERVAL.LEFT_1.value,
                                                 game_relations.HABIT_HONOR_INTERVAL.RIGHT_1.value],
                restrictions.GROUP.HABIT_PEACEFULNESS: [game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1.value,
                                                        game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1.value],
                restrictions.GROUP.ARCHETYPE: [record.value for record in game_relations.ARCHETYPE.records],
                restrictions.GROUP.UPBRINGING: [record.value for record in tt_beings_relations.UPBRINGING.records],
                restrictions.GROUP.FIRST_DEATH: [record.value for record in tt_beings_relations.FIRST_DEATH.records],
                restrictions.GROUP.AGE: [record.value for record in tt_beings_relations.AGE.records]}}

        for variable_value, restriction_id in current_restrictions:
            if variable_value not in allowed_reistrictions:
                raise django_forms.ValidationError('Ограничения для переменной «{}» нельзя использовать в этой фразе'.format(variable_value))

            restriction = storage.restrictions[restriction_id]

            if restriction.group not in allowed_reistrictions[variable_value]:
                field_name = 'restriction_%s_%d' % (variable_value, restriction.group.value)
                message_template = 'Тип ограничений «{}» для переменной «{}» нельзя использовать в этой фразе'
                raise django_forms.ValidationError({field_name: message_template.format(restriction.group.text, variable_value)})

            if restriction.external_id not in allowed_reistrictions[variable_value][restriction.group]:
                field_name = 'restriction_%s_%d' % (variable_value, restriction.group.value)
                message_template = 'Текущие занчения типа  ограничений «{}» для переменной «{}» нельзя использовать в этой фразе'
                raise django_forms.ValidationError({field_name: message_template.format(restriction.group.text, variable_value)})

        for template_model in models.Template.objects.filter(key=self.key).iterator():
            template = prototypes.TemplatePrototype(template_model)

            if template.id == self.template_id:
                continue

            if template.raw_restrictions == frozenset(current_restrictions):
                message_template = 'Фраза с такими ограничениями уже есть, её идентификатор: {}. Не может быть двух фраз истории с одинаковыми ограничениями.'
                raise django_forms.ValidationError(message_template.format(template.id))

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

for group in lexicon_groups_relations.LEXICON_GROUP.records:
    keys = []
    for key in lexicon_keys.LEXICON_KEY.records:
        if key.group != group:
            continue
        keys.append((key, key.text))
    keys.sort(key=lambda x: x[1])
    KEY_CHOICES.append((group.text, keys))


class TemplateKeyForm(dext_forms.Form):
    key = django_forms.TypedChoiceField(label='Тип фразы', choices=KEY_CHOICES, coerce=lexicon_keys.LEXICON_KEY.get_from_name)


class LoadDictionaryForm(dext_forms.Form):
    words = dext_fields.TextField(label='Данные словаря')

    def clean_words(self):
        data = self.cleaned_data.get('words')

        if data is None:
            raise django_forms.ValidationError('Нет данных', code='not_json')

        try:
            words_data = s11n.from_json(data)
        except ValueError:
            raise django_forms.ValidationError('Данные должны быть в формате JSON', code='not_json')

        try:
            words = [utg_words.Word.deserialize(word_data) for word_data in words_data.get('words')]
        except:
            raise django_forms.ValidationError('Неверный формат описания слов', code='wrong_words_format')

        return words
