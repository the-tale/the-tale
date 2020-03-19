
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    place = utils_fields.ChoiceField(label='Город')
    new_race = utils_fields.TypedChoiceField(label='Новая раса',
                                             choices=sorted([(record, record.multiple_text) for record in game_relations.RACE.records], key=lambda g: g[1]),
                                             coerce=game_relations.RACE.get_from_name)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()

    def clean(self):
        cleaned_data = super(BaseForm, self).clean()

        place = places_storage.places.get(int(cleaned_data['place']))
        race = cleaned_data.get('new_race')

        if race:
            if race == place.race:
                raise django_forms.ValidationError('Город уже принадлежит выбранной расе.')

            if not any(race == person.race for person in place.persons):
                raise django_forms.ValidationError('В городе должен быть Мастер соответствующей расы.')

        return cleaned_data


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceRace(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_CHANGE_RACE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Изменение расы города'
    DESCRIPTION = 'Изменяет расу города. В городе должен быть Мастер соответствующей расы.'

    def __init__(self, new_race=None, old_race=None, **kwargs):
        super(PlaceRace, self).__init__(**kwargs)
        self.new_race = new_race
        self.old_race = old_race

    def user_form_initials(self):
        data = super(PlaceRace, self).user_form_initials()
        data['new_race'] = self.new_race
        return data

    def initialize_with_form(self, user_form):
        super(PlaceRace, self).initialize_with_form(user_form)
        self.new_race = user_form.c.new_race
        self.old_race = self.place.race

    def has_meaning(self):
        return ((self.place.race != self.new_race) and
                any(self.new_race == person.race for person in self.place.persons))

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.race = self.new_race
            places_logic.save_place(self.place)

    def serialize(self):
        data = super(PlaceRace, self).serialize()
        data['new_race'] = self.new_race.value
        data['old_race'] = self.old_race.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceRace, cls).deserialize(data)
        obj.new_race = game_relations.RACE(data['new_race'])
        obj.old_race = game_relations.RACE(data['old_race'])
        return obj
