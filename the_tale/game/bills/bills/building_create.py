# coding: utf-8

from textgen.words import Noun

from dext.forms import fields

from game.game_info import GENDER

from game.balance.enums import RACE

from game.persons.prototypes import PersonPrototype
from game.persons.relations import PERSON_TYPE
from game.persons.storage import persons_storage

from game.map.places.prototypes import BuildingPrototype

from game.bills.relations import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Персонаж')

    def __init__(self, choosen_person_id, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices()


class ModeratorForm(BaseModeratorForm):
    pass


class BuildingCreate(object):

    type = BILL_TYPE.BUILDING_CREATE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_create_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_create_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_create_show.html'

    CAPTION = u'Закон о возведение постройки'
    DESCRIPTION = u'Возводит здание, принадлежащее выбранному персонажу (и соответствующее его профессии). Один персонаж может иметь только одну постройку.'

    def __init__(self, person_id=None, old_place_name_forms=None):
        self.old_place_name_forms = old_place_name_forms
        self.person_id = person_id

        if person_id is not None:
            self.person_name = self.person.name
            self.person_race = self.person.race
            self.person_type = self.person.type
            self.person_gender = self.person.gender

    @property
    def person(self):
        return persons_storage[self.person_id]

    @property
    def old_place_name(self):
        return self.old_place_name_forms.normalized

    @property
    def person_race_verbose(self):
        return RACE._ID_TO_TEXT[self.person_race]

    @property
    def person_gender_verbose(self):
        return GENDER._ID_TO_TEXT[self.person_gender]

    @property
    def user_form_initials(self):
        return {'person': self.person_id}

    @property
    def moderator_form_initials(self):
        return {}

    def initialize_with_user_data(self, user_form):
        self.person_id = int(user_form.c.person)
        self.old_place_name_forms = self.person.place.normalized_name

        self.person_name = self.person.name
        self.person_race = self.person.race
        self.person_type = self.person.type
        self.person_gender = self.person.gender


    def initialize_with_moderator_data(self, moderator_form):
        pass

    @classmethod
    def get_user_form_create(cls, post=None):
        return UserForm(None, post)

    def get_user_form_update(self, post=None, initial=None):
        if initial:
            return UserForm(self.person_id, initial=initial)
        return  UserForm(self.person_id, post)

    def apply(self):
        BuildingPrototype.create(self.person)


    def serialize(self):
        return {'type': self.type.name.lower(),
                'person_id': self.person_id,
                'person_name': self.person_name,
                'person_race': self.person_race,
                'person_type': self.person_type.value,
                'person_gender': self.person_gender,
                'old_place_name_forms': self.old_place_name_forms.serialize()}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.person_id = data['person_id']
        obj.person_name = data['person_name']
        obj.person_race = data['person_race']
        obj.person_type = PERSON_TYPE(data['person_type'])
        obj.person_gender = data['person_gender']

        obj.old_place_name_forms = Noun.deserialize(data['old_place_name_forms'])

        return obj
