
import smart_imports


smart_imports.all()


class EmissaryForm(dext_forms.Form):

    gender = dext_fields.TypedChoiceField(label='пол',
                                          choices=game_relations.GENDER.choices(),
                                          coerce=game_relations.GENDER.get_from_name)

    race = dext_fields.TypedChoiceField(label='раса',
                                        choices=game_relations.RACE.choices(),
                                        coerce=game_relations.RACE.get_from_name)

    place = dext_fields.TypedChoiceField(label='Город',
                                         choices=places_storage.places.get_choices,
                                         coerce=int)


class MoveEmissaryForm(dext_forms.Form):
    place = dext_fields.TypedChoiceField(label='Город',
                                         choices=places_storage.places.get_choices,
                                         coerce=int)
