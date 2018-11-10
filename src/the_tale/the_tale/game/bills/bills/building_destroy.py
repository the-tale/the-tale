
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    person = dext_fields.ChoiceField(label='Житель')

    def __init__(self, choosen_person_id, *args, **kwargs):  # pylint: disable=W0613
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = persons_objects.Person.form_choices(predicate=self._person_has_building)

    @classmethod
    def _person_has_building(cls, place, person):  # pylint: disable=W0613
        return places_storage.buildings.get_by_person_id(person.id) is not None


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class BuildingDestroy(base_person_bill.BasePersonBill):
    type = relations.BILL_TYPE.BUILDING_DESTROY

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Разрушение постройки'
    DESCRIPTION = 'Разрушает здание, принадлежащее выбранному Мастеру.'

    def __init__(self, building_name_forms=None, **kwargs):
        super(BuildingDestroy, self).__init__(**kwargs)

        self.building_name_forms = building_name_forms

        if self.building_name_forms is None:
            building = places_storage.buildings.get_by_person_id(self.person_id)
            if building is not None:
                self.building_name_forms = building.utg_name

    @property
    def base_name(self): return self.building_name_forms.normal_form()

    @property
    def building(self): return places_storage.buildings.get_by_person_id(self.person.id)

    def has_meaning(self):
        return self.building and not self.building.state.is_DESTROYED

    def apply(self, bill=None):
        if self.has_meaning():
            places_logic.destroy_building(self.building)

    def initialize_with_form(self, user_form):
        super(BuildingDestroy, self).initialize_with_form(user_form)

        building = places_storage.buildings.get_by_person_id(self.person_id)
        if building is not None:
            self.building_name_forms = building.utg_name

    def serialize(self):
        data = super(BuildingDestroy, self).serialize()
        data['building_name_forms'] = self.building_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingDestroy, cls).deserialize(data)

        if 'building_name_forms' in data:
            obj.building_name_forms = utg_words.Word.deserialize(data['building_name_forms'])
        else:
            obj.building_name_forms = game_names.generator().get_fast_name('название утрачено')

        return obj
