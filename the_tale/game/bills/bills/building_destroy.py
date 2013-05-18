# coding: utf-8

from dext.forms import fields

from game.persons.prototypes import PersonPrototype

from game.map.places.storage import buildings_storage

from game.bills.relations import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm
from game.bills.bills.base_person_bill import BasePersonBill

class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Персонаж')

    def __init__(self, choosen_person_id, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(predicate=self._person_has_building)

    @classmethod
    def _person_has_building(cls, place, person):
        return buildings_storage.get_by_person_id(person.id) is not None


class ModeratorForm(BaseModeratorForm):
    pass


class BuildingDestroy(BasePersonBill):

    type = BILL_TYPE.BUILDING_DESTROY

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_destroy_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_destroy_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_destroy_show.html'

    CAPTION = u'Разрушение постройки'
    DESCRIPTION = u'Разрушает здание, принадлежащее выбранному персонажу.'

    def apply(self):
        building = buildings_storage.get_by_person_id(self.person.id)

        if building is None or building.state._is_DESTROYED:
            return

        building.destroy()
