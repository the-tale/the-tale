# coding: utf-8

from dext.forms import fields

from game.persons.prototypes import PersonPrototype

from game.map.places.prototypes import BuildingPrototype

from game.bills.relations import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm
from game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Персонаж')

    def __init__(self, choosen_person_id, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(predicate=lambda place, person: not person.has_building)


class ModeratorForm(BaseModeratorForm):
    pass


class BuildingCreate(BasePersonBill):

    type = BILL_TYPE.BUILDING_CREATE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_create_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_create_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_create_show.html'

    CAPTION = u'Закон о возведении постройки'
    DESCRIPTION = u'Возводит здание, принадлежащее выбранному персонажу (и соответствующее его профессии). Один персонаж может иметь только одну постройку. Помните, что для поддержания работы здания потребуется участие игроков, иначе оно обветшает и разрушится.'

    def apply(self):
        if self.person is None or self.person.out_game:
            return

        BuildingPrototype.create(self.person)
