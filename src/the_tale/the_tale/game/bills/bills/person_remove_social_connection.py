# coding: utf-8

from django.forms import ValidationError

from dext.forms import fields

from utg import words as utg_words

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c

from the_tale.game.persons import logic as persons_logic
from the_tale.game.persons import objects as persons_objects
from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import relations as persons_relations

from the_tale.game.places import storage as places_storage

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, ModeratorFormMixin
from the_tale.game.bills.bills.base_bill import BaseBill


class BaseForm(BaseUserForm):
    person_1 = fields.ChoiceField(label='Первый Мастер')
    person_2 = fields.ChoiceField(label='Второй Мастер')

    def __init__(self, person_1_id, person_2_id, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['person_1'].choices = persons_objects.Person.form_choices(choosen_person=persons_storage.persons.get(person_1_id),
                                                                              predicate=self.person_filter)
        self.fields['person_2'].choices = persons_objects.Person.form_choices(choosen_person=persons_storage.persons.get(person_2_id),
                                                                              predicate=self.person_filter)

    def person_filter(self, place, person):
        return persons_storage.social_connections.has_connections(person)


    def clean(self):
        cleaned_data = super(BaseForm, self).clean()

        if 'person_1' not in cleaned_data or 'person_2' not in cleaned_data:
            return cleaned_data # error in one of that filed, no need to continue cleaning

        person_1 = persons_storage.persons[int(cleaned_data['person_1'])]
        person_2 = persons_storage.persons[int(cleaned_data['person_2'])]

        if person_1.id == person_2.id:
            raise ValidationError('Необхоимо выбрать двух разных Мастеров')

        connection = persons_storage.social_connections.get_connection(person_1, person_2)

        if connection is None:
            raise ValidationError('Мастера не имеют связи')

        if not connection.can_be_removed():
            raise ValidationError('Эту связь пока нельзя разорвать, дождитесь пока она просуществует минимально допустимое время')

        return cleaned_data


class UserForm(BaseForm):

    def __init__(self, person_1_id, person_2_id, owner_id, *args, **kwargs):
        super(UserForm, self).__init__(person_1_id, person_2_id, *args, **kwargs)
        self.owner_id = owner_id


    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        if 'person_1' not in cleaned_data or 'person_2' not in cleaned_data:
            return cleaned_data # error in one of that filed, no need to continue cleaning

        person_1 = persons_storage.persons[int(cleaned_data['person_1'])]
        person_2 = persons_storage.persons[int(cleaned_data['person_2'])]

        if (not person_1.politic_power.is_in_inner_circle(self.owner_id) and
            not person_2.politic_power.is_in_inner_circle(self.owner_id)):
            raise ValidationError('Вы не состоите в ближнем круге ни одного из Мастеров')

        return cleaned_data


class ModeratorForm(BaseForm, ModeratorFormMixin):
    pass


class PersonRemoveSocialConnection(BaseBill):
    type = relations.BILL_TYPE.PERSON_REMOVE_SOCIAL_CONNECTION

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Удалить социальную связь'
    DESCRIPTION = 'Социальную связь между Мастерами можно удалить, помирив конкурентов или рассорив партнёров. Выдвинуть закон может только Хранитель героя из ближнего круга одного из Мастеров. Герой должен быть в ближнем круге на момент создания закона и/или его редактирования.'

    def __init__(self,
                 person_1_id=None,
                 person_2_id=None,
                 place_1_id=None,
                 place_2_id=None,
                 old_place_1_name=None,
                 old_place_2_name=None,
                 connection_type=None):
        super(PersonRemoveSocialConnection, self).__init__()

        self.person_1_id = person_1_id
        self.person_2_id = person_2_id

        self.place_1_id = place_1_id
        self.place_2_id = place_2_id

        self.old_place_1_name = old_place_1_name
        self.old_place_2_name = old_place_2_name

        self.connection_type = connection_type

        if self.place_1_id is None and self.person_1_id is not None:
            self.place_1_id = self.person_1.place.id

        if self.place_2_id is None and self.person_2_id is not None:
            self.place_2_id = self.person_2.place.id

        if self.old_place_1_name is None and self.place_1_id is not None:
            self.old_place_1_name = self.place_1.utg_name

        if self.old_place_2_name is None and self.place_2_id is not None:
            self.old_place_2_name = self.place_2.utg_name

        if self.connection_type is None and self.person_1_id is not None and self.person_2_id is not None:
            self.connection_type = persons_storage.social_connections.get_connection_type(self.person_1, self.person_2)


    @property
    def person_1(self): return persons_storage.persons[self.person_1_id]

    @property
    def person_2(self): return persons_storage.persons[self.person_2_id]

    @property
    def place_1(self): return places_storage.places[self.place_1_id]

    @property
    def place_2(self): return places_storage.places[self.place_2_id]

    @property
    def actors(self): return [self.place_1, self.place_2, self.person_1, self.person_2]

    def user_form_initials(self):
        return {'person_1': self.person_1_id,
                'person_2': self.person_2_id}

    @classmethod
    def get_user_form_create(cls, post=None, owner_id=None):
        return cls.UserForm(None, None, owner_id, post) #pylint: disable=E1102


    def get_user_form_update(self, post=None, initial=None, owner_id=None):
        if initial:
            return self.UserForm(self.person_1_id, self.person_2_id, owner_id, initial=initial) #pylint: disable=E1102
        return  self.UserForm(self.person_1_id, self.person_2_id, owner_id, post) #pylint: disable=E1102


    def get_moderator_form_update(self, post=None, initial=None):
        if initial:
            return self.ModeratorForm(self.person_1_id, self.person_2_id, initial=initial) #pylint: disable=E1102
        return  self.ModeratorForm(self.person_1_id, self.person_2_id, post) #pylint: disable=E1102

    @property
    def place_1_name_changed(self):
        return self.old_place_1_name != self.place_1.utg_name

    @property
    def place_2_name_changed(self):
        return self.old_place_2_name != self.place_2.utg_name

    @property
    def place_1_name(self): return self.place_1.name

    @property
    def place_2_name(self): return self.place_2.name

    def initialize_with_form(self, user_form):
        self.person_1_id = int(user_form.c.person_1)
        self.person_2_id = int(user_form.c.person_2)

        self.place_1_id = self.person_1.place.id
        self.place_2_id = self.person_2.place.id

        self.old_place_1_name = self.place_1.utg_name
        self.old_place_2_name = self.place_2.utg_name

        self.connection_type = persons_storage.social_connections.get_connection_type(self.person_1, self.person_2)

    def has_meaning(self):
        if not persons_storage.social_connections.is_connected(self.person_1, self.person_2):
            return False

        return True


    def apply(self, bill=None):
        if self.has_meaning():
            connection = persons_storage.social_connections.get_connection(self.person_1, self.person_2)
            persons_logic.remove_connection(connection)


    def serialize(self):
        return {'type': self.type.name.lower(),
                'person_1_id': self.person_1_id,
                'person_2_id': self.person_2_id,
                'place_1_id': self.place_1_id,
                'place_2_id': self.place_2_id,
                'old_place_1_name': self.old_place_1_name.serialize(),
                'old_place_2_name': self.old_place_2_name.serialize(),
                'connection_type': self.connection_type.value}

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        obj.person_1_id = data['person_1_id']
        obj.person_2_id = data['person_2_id']

        obj.place_1_id = data['place_1_id']
        obj.place_2_id = data['place_2_id']

        obj.old_place_1_name = utg_words.Word.deserialize(data['old_place_1_name'])
        obj.old_place_2_name = utg_words.Word.deserialize(data['old_place_2_name'])

        obj.connection_type = persons_relations.SOCIAL_CONNECTION_TYPE(data['connection_type'])

        return obj
