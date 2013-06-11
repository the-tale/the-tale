# coding: utf-8

from dext.forms import fields

from textgen.words import Noun, WordBase

from common.utils.forms import SimpleWordField

from game.persons.prototypes import PersonPrototype

from game.map.places.storage import buildings_storage

from game.bills.relations import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm
from game.bills.bills.base_person_bill import BasePersonBill

class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Персонаж')
    new_name = fields.CharField(label=u'Новое название')

    def __init__(self, choosen_person_id, *args, **kwargs): # pylint: disable=W0613
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(predicate=self._person_has_building)

    @classmethod
    def _person_has_building(cls, place, person): # pylint: disable=W0613
        return buildings_storage.get_by_person_id(person.id) is not None


class ModeratorForm(BaseModeratorForm):
    new_building_name_forms = SimpleWordField(label=u'Формы названия')


class BuildingRenaming(BasePersonBill):

    type = BILL_TYPE.BUILDING_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_renaming_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_renaming_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_renaming_show.html'

    CAPTION = u'Переименование постройки'
    DESCRIPTION = u'Изменяет название постройки, принадлежащей выбранному персонажу.'

    def __init__(self, old_building_name_forms=None, new_building_name_forms=None, **kwargs):
        super(BuildingRenaming, self).__init__(**kwargs)

        self.old_building_name_forms = old_building_name_forms
        self.new_building_name_forms = new_building_name_forms

        if self.old_building_name_forms is None:
            building = buildings_storage.get_by_person_id(self.person_id)
            if building is not None:
                self.old_building_name_forms = building.normalized_name

    @property
    def old_name(self): return self.old_building_name_forms.normalized

    @property
    def new_name(self): return self.new_building_name_forms.normalized

    def apply(self):
        building = buildings_storage.get_by_person_id(self.person.id)

        if building is None or building.state._is_DESTROYED:
            return

        building.set_name_forms(self.new_building_name_forms)
        building.save()


    @property
    def user_form_initials(self):
        initials = super(BuildingRenaming, self).user_form_initials
        initials.update({'new_name': self.new_name})
        return initials

    @property
    def moderator_form_initials(self):
        initials = super(BuildingRenaming, self).moderator_form_initials
        initials.update({'new_building_name_forms': self.new_building_name_forms.serialize()})
        return initials

    def initialize_with_user_data(self, user_form):
        super(BuildingRenaming, self).initialize_with_user_data(user_form)
        self.new_building_name_forms = Noun.fast_construct(user_form.c.new_name)

        building = buildings_storage.get_by_person_id(self.person_id)
        if building is not None:
            self.old_building_name_forms = building.normalized_name

    def initialize_with_moderator_data(self, moderator_form):
        super(BuildingRenaming, self).initialize_with_moderator_data(moderator_form)
        self.new_building_name_forms = moderator_form.c.new_building_name_forms


    def serialize(self):
        data = super(BuildingRenaming, self).serialize()
        data['old_building_name_forms'] = self.old_building_name_forms.serialize()
        data['new_building_name_forms'] = self.new_building_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingRenaming, cls).deserialize(data)
        obj.old_building_name_forms = WordBase.deserialize(data['old_building_name_forms'])
        obj.new_building_name_forms = WordBase.deserialize(data['new_building_name_forms'])

        return obj
