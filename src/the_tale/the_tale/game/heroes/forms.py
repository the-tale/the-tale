
import smart_imports

smart_imports.all()


NAME_REGEX = re.compile(conf.settings.NAME_REGEX)


class EditNameForm(dext_forms.Form):

    race = dext_fields.TypedChoiceField(label='раса',
                                        choices=game_relations.RACE.choices(),
                                        coerce=game_relations.RACE.get_from_name)
    gender = dext_fields.TypedChoiceField(label='пол',
                                          choices=game_relations.GENDER.choices(),
                                          coerce=game_relations.GENDER.get_from_name)
    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN,
                                       widget_class=linguistics_forms.SimpleNounWidget,
                                       label='имя',
                                       skip_markers=(utg_relations.NOUN_FORM.COUNTABLE, utg_relations.NUMBER.PLURAL),
                                       show_properties=False)

    def clean(self):
        cleaned_data = super(EditNameForm, self).clean()

        name = cleaned_data.get('name')

        if name is not None:
            for name_form in cleaned_data['name'].forms:
                if len(name_form) > models.Hero.MAX_NAME_LENGTH:
                    raise django_forms.ValidationError('Слишком длинное имя, максимальное число символов: %d' % models.Hero.MAX_NAME_LENGTH)

                if len(name_form) < conf.settings.NAME_MIN_LENGHT:
                    raise django_forms.ValidationError('Слишком короткое имя, минимальное число символов: %d' %
                                                       conf.settings.NAME_MIN_LENGHT)

                if NAME_REGEX.match(name_form) is None:
                    raise django_forms.ValidationError('Имя героя может содержать только следующие символы: %s' %
                                                       conf.settings.NAME_SYMBOLS_DESCRITION)

            name.properties = name.properties.clone(cleaned_data['gender'].utg_id,
                                                    utg_relations.NUMBER.SINGULAR)

        return cleaned_data

    @classmethod
    def get_initials(cls, hero):
        return {'gender': hero.gender,
                'race': hero.race,
                'name': hero.utg_name}
