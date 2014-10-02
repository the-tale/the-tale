# coding: utf-8

from utg import words as utg_words

from the_tale.game import names

from the_tale.game.relations import GENDER, RACE

from the_tale.game.persons.relations import PERSON_TYPE
from the_tale.game.persons.storage import persons_storage

from the_tale.game.map.places.storage import places_storage

from the_tale.game.bills.bills.base_bill import BaseBill


class BasePersonBill(BaseBill):

    type = None

    UserForm = None
    ModeratorForm = None

    USER_FORM_TEMPLATE = None
    MODERATOR_FORM_TEMPLATE = None
    SHOW_TEMPLATE = None

    CAPTION = None
    DESCRIPTION = None

    def __init__(self, person_id=None, old_place_name_forms=None, place_id=None):
        super(BasePersonBill, self).__init__()
        self.old_place_name_forms = old_place_name_forms
        self.person_id = person_id
        self.place_id = place_id

        if self.person is not None:
            self.person_name = self.person.name
            self.person_race = self.person.race
            self.person_type = self.person.type
            self.person_gender = self.person.gender
            self.place_id = self.person.place.id

    @property
    def person(self):
        return persons_storage.get(self.person_id)

    @property
    def place_name_changed(self):
        return self.old_place_name != self.place.name

    @property
    def place(self):
        return places_storage.get(self.place_id)

    @property
    def actors(self): return [self.place]

    @property
    def old_place_name(self):
        return self.old_place_name_forms.normal_form()

    @property
    def person_race_verbose(self):
        return self.person_race.text

    @property
    def person_gender_verbose(self):
        return self.person_gender.text

    @property
    def user_form_initials(self):
        return {'person': self.person_id}

    def initialize_with_user_data(self, user_form):
        self.person_id = int(user_form.c.person)
        self.old_place_name_forms = self.person.place.utg_name

        self.person_name = self.person.name
        self.person_race = self.person.race
        self.person_type = self.person.type
        self.person_gender = self.person.gender
        self.place_id = self.person.place.id

    @classmethod
    def get_user_form_create(cls, post=None):
        return cls.UserForm(None, post) #pylint: disable=E1102

    def get_user_form_update(self, post=None, initial=None):
        if initial:
            return self.UserForm(self.person_id, initial=initial) #pylint: disable=E1102
        return  self.UserForm(self.person_id, post) #pylint: disable=E1102

    def apply(self, bill=None):
        raise NotImplementedError

    def serialize(self):
        return {'type': self.type.name.lower(),
                'person_id': self.person_id,
                'person_name': self.person_name,
                'person_race': self.person_race.value,
                'person_type': self.person_type.value,
                'person_gender': self.person_gender.value,
                'place_id': self.place_id,
                'old_place_name_forms': self.old_place_name_forms.serialize()}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.person_id = data['person_id']
        obj.person_name = data['person_name']
        obj.person_race = RACE(data['person_race'])
        obj.person_type = PERSON_TYPE(data['person_type'])
        obj.person_gender = GENDER(data['person_gender'])
        obj.place_id = data['place_id']

        if 'old_place_name_forms' in data:
            obj.old_place_name_forms = utg_words.Word.deserialize(data['old_place_name_forms'])
        else:
            obj.old_place_name_forms = names.generator.get_fast_name(u'название неизвестно')

        return obj
