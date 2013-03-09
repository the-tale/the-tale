# coding: utf-8

from django.forms import ValidationError

from dext.forms import fields

from textgen.words import Noun

from game.map.places.models import Place

from game.bills.models import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm

from game.map.places.storage import places_storage

class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    new_name = fields.CharField(label=u'Новое название', max_length=Place.MAX_NAME_LENGTH)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()


class ModeratorForm(BaseModeratorForm):

    name_forms = fields.JsonField(label=u'Формы названия')

    def clean_name_forms(self):
        data = self.cleaned_data['name_forms']

        noun = Noun.deserialize(data)

        if not noun.is_valid:
            raise ValidationError(u'неверное описание форм существительного')

        return noun


class PlaceRenaming(object):

    type = BILL_TYPE.PLACE_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_renaming_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_renaming_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_renaming_show.html'

    CAPTION = u'Закон о переименовании города'
    DESCRIPTION = u'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, place_id=None, base_name=None, name_forms=None, old_name_forms=None):
        self.place_id = place_id
        self.name_forms = name_forms
        self.old_name_forms = old_name_forms

        if self.name_forms is None and base_name is not None:
            self.name_forms = Noun.fast_construct(base_name)

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.normalized_name

    @property
    def place(self):
        return places_storage[self.place_id]

    @property
    def base_name(self): return self.name_forms.normalized

    @property
    def old_name(self): return self.old_name_forms.normalized

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'new_name': self.base_name}

    @property
    def moderator_form_initials(self):
        return {'name_forms': self.name_forms.serialize()}

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.old_name_forms = self.place.normalized_name
        self.name_forms = Noun.fast_construct(user_form.c.new_name)

    def initialize_with_moderator_data(self, moderator_form):
        self.name_forms = moderator_form.c.name_forms

    @classmethod
    def get_user_form_create(cls, post=None):
        return cls.UserForm(post)

    def get_user_form_update(self, post=None, initial=None):
        if initial:
            return self.UserForm(initial=initial)
        return  self.UserForm(post)


    def apply(self):
        self.place.set_name_forms(self.name_forms)
        self.place.save()
        places_storage.update_version()


    def serialize(self):
        return {'type': self.type.name.lower(),
                'old_name_forms': self.old_name_forms.serialize(),
                'name_forms': self.name_forms.serialize(),
                'place_id': self.place_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        if 'old_name_forms' in data:
            obj.old_name_forms = Noun.deserialize(data['old_name_forms'])
        else:
            obj.old_name_forms = Noun.fast_construct(u'название неизвестно')

        obj.name_forms = Noun.deserialize(data['name_forms'])
        obj.place_id = data['place_id']

        return obj
