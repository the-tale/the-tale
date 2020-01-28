
import smart_imports


smart_imports.all()


class EmissaryForm(utils_forms.Form):

    gender = utils_fields.TypedChoiceField(label='пол',
                                           choices=game_relations.GENDER.choices(),
                                           coerce=game_relations.GENDER.get_from_name)

    race = utils_fields.TypedChoiceField(label='раса',
                                         choices=game_relations.RACE.choices(),
                                         coerce=game_relations.RACE.get_from_name)

    place = utils_fields.TypedChoiceField(label='Город',
                                          choices=places_storage.places.get_choices,
                                          coerce=int)


class EmptyEventForm(utils_forms.Form):

    period = utils_fields.TypedChoiceField(label='длительность',
                                           choices=[],
                                           coerce=int)

    def __init__(self, period_choices, *argv, **kwargs):
        super().__init__(*argv, **kwargs)

        self.fields['period'].choices = period_choices
        self.fields['period'].widget.attrs['class'] = 'input-xxlarge'


class RelocateEventForm(EmptyEventForm):

    place = utils_fields.TypedChoiceField(label='Город',
                                          choices=[],
                                          coerce=int)

    def __init__(self, current_place_id, *argv, **kwargs):
        super().__init__(*argv, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices(exclude=[current_place_id])


class RenameEventForm(EmptyEventForm):

    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN,
                                       widget_class=linguistics_forms.SimpleNounWidget,
                                       label='имя',
                                       skip_markers=(utg_relations.NOUN_FORM.COUNTABLE, utg_relations.NUMBER.PLURAL),
                                       show_properties=False)
