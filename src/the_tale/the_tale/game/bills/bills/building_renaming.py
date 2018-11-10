
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    person = dext_fields.ChoiceField(label='Житель')
    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))

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


class BuildingRenaming(base_person_bill.BasePersonBill):
    type = relations.BILL_TYPE.BUILDING_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Переименование постройки'
    DESCRIPTION = 'Изменяет название постройки, принадлежащей выбранному Мастеру.'

    def __init__(self, old_building_name_forms=None, new_building_name_forms=None, **kwargs):
        super(BuildingRenaming, self).__init__(**kwargs)

        self.old_building_name_forms = old_building_name_forms
        self.new_building_name_forms = new_building_name_forms

        if self.old_building_name_forms is None:
            building = places_storage.buildings.get_by_person_id(self.person_id)
            if building is not None:
                self.old_building_name_forms = building.utg_name

    @property
    def old_name(self): return self.old_building_name_forms.normal_form()

    @property
    def new_name(self): return self.new_building_name_forms.normal_form()

    @property
    def building(self): return places_storage.buildings.get_by_person_id(self.person.id)

    def has_meaning(self):
        return self.building and not self.building.state.is_DESTROYED and self.building.utg_name != self.new_building_name_forms

    def apply(self, bill=None):
        if self.has_meaning():
            self.building.set_utg_name(self.new_building_name_forms)
            places_logic.save_building(self.building)

    def user_form_initials(self):
        initials = super(BuildingRenaming, self).user_form_initials()
        initials['name'] = self.new_building_name_forms
        return initials

    def initialize_with_form(self, user_form):
        super(BuildingRenaming, self).initialize_with_form(user_form)
        self.new_building_name_forms = user_form.c.name

        building = places_storage.buildings.get_by_person_id(self.person_id)
        if building is not None:
            self.old_building_name_forms = building.utg_name

    def serialize(self):
        data = super(BuildingRenaming, self).serialize()
        data['old_building_name_forms'] = self.old_building_name_forms.serialize()
        data['new_building_name_forms'] = self.new_building_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingRenaming, cls).deserialize(data)
        obj.old_building_name_forms = utg_words.Word.deserialize(data['old_building_name_forms'])
        obj.new_building_name_forms = utg_words.Word.deserialize(data['new_building_name_forms'])

        return obj
