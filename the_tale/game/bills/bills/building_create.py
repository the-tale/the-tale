# coding: utf-8

from dext.forms import fields

from textgen.words import Noun, WordBase

from common.utils.forms import SimpleWordField

from game.persons.prototypes import PersonPrototype

from game.map.places.prototypes import BuildingPrototype

from game.bills.relations import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm
from game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Персонаж')
    name = fields.CharField(label=u'Название')

    def __init__(self, choosen_person_id, *args, **kwargs):  # pylint: disable=W0613
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(predicate=lambda place, person: not person.has_building)


class ModeratorForm(BaseModeratorForm):
    building_name_forms = SimpleWordField(label=u'Формы названия')


class BuildingCreate(BasePersonBill):

    type = BILL_TYPE.BUILDING_CREATE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_create_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_create_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_create_show.html'

    CAPTION = u'Возведение постройки'
    # TODO: remove hardcoded url
    DESCRIPTION = u'Возводит здание, принадлежащее выбранному персонажу (и соответствующее его профессии). Один персонаж может иметь только одну постройку. Помните, что для поддержания работы здания потребуется участие игроков, иначе оно обветшает и разрушится. О типах зданий можно узнать в <a href="/guide/persons">Путеводителе</a>.'

    def __init__(self, base_name=None, building_name_forms=None, **kwargs):
        super(BuildingCreate, self).__init__(**kwargs)

        self.building_name_forms = building_name_forms

        if self.building_name_forms is None and base_name is not None:
            self.building_name_forms = Noun.fast_construct(base_name)

    @property
    def base_name(self): return self.building_name_forms.normalized

    def apply(self):
        if self.person is None or self.person.out_game:
            return

        BuildingPrototype.create(self.person, name_forms=self.building_name_forms)

    @property
    def user_form_initials(self):
        initials = super(BuildingCreate, self).user_form_initials
        initials.update({'name': self.base_name})
        return initials

    @property
    def moderator_form_initials(self):
        initials = super(BuildingCreate, self).moderator_form_initials
        initials.update({'building_name_forms': self.building_name_forms.serialize()})
        return initials

    def initialize_with_user_data(self, user_form):
        super(BuildingCreate, self).initialize_with_user_data(user_form)
        self.building_name_forms = Noun.fast_construct(user_form.c.name)

    def initialize_with_moderator_data(self, moderator_form):
        super(BuildingCreate, self).initialize_with_moderator_data(moderator_form)
        self.building_name_forms = moderator_form.c.building_name_forms

    def serialize(self):
        data = super(BuildingCreate, self).serialize()
        data['building_name_forms'] = self.building_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingCreate, cls).deserialize(data)

        if 'building_name_forms' in data:
            obj.building_name_forms = WordBase.deserialize(data['building_name_forms'])
        else:
            obj.building_name_forms = Noun.fast_construct(u'название неизвестно')

        return obj
