
import smart_imports

smart_imports.all()


class EditNameForm(utils_forms.Form):

    race = utils_fields.TypedChoiceField(label='раса',
                                         choices=game_relations.RACE.choices(),
                                         coerce=game_relations.RACE.get_from_name)
    gender = utils_fields.TypedChoiceField(label='пол',
                                           choices=game_relations.GENDER.choices(),
                                           coerce=game_relations.GENDER.get_from_name)
    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN,
                                       widget_class=linguistics_forms.SimpleNounWidget,
                                       label='имя',
                                       skip_markers=(utg_relations.NOUN_FORM.COUNTABLE, utg_relations.NUMBER.PLURAL),
                                       show_properties=False)

    description = utils_bbcode.BBField(required=False,
                                       label='Несколько слов о вашем герое',
                                       max_length=conf.settings.MAX_HERO_DESCRIPTION_LENGTH)

    def clean(self):
        cleaned_data = super(EditNameForm, self).clean()

        name = cleaned_data.get('name')

        if name is not None:
            success, message = logic.validate_name(cleaned_data['name'].forms)

            if not success:
                raise django_forms.ValidationError(message)

            game_names.sync_properties(name, cleaned_data['gender'])

        return cleaned_data

    @classmethod
    def get_initials(cls, hero):
        return {'gender': hero.gender,
                'race': hero.race,
                'name': hero.utg_name,
                'description': logic.get_hero_description(hero.id)}
