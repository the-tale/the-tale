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
        self.fields['place'].choices = [(place.id, place.name) for place in sorted(places_storage.all(), key=lambda p: p.name)]


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
    type_str = BILL_TYPE._ID_TO_STR[BILL_TYPE.PLACE_RENAMING].lower()

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_renaming_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_renaming_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_renaming_show.html'

    CAPTION = u'Закон о переименовании города'
    DESCRIPTION = u'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, place_id=None, base_name=None, name_forms=None, old_name=None):
        self.place_id = place_id
        self.base_name = base_name
        self.old_name = old_name
        self.name_forms = name_forms

        if self.name_forms is None and self.base_name is not None:
            self.name_forms = Noun(normalized=self.base_name.lower(),
                                   forms=[self.base_name] * Noun.FORMS_NUMBER,
                                   properties=(u'мр',))

    @property
    def place(self):
        return places_storage[self.place_id]

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'new_name': self.base_name}

    @property
    def moderator_form_initials(self):
        return {'name_forms': self.name_forms.serialize()}

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.base_name = user_form.c.new_name
        self.old_name = self.place.name

        self.name_forms = Noun(normalized=self.base_name.lower(),
                               forms=[self.base_name] * Noun.FORMS_NUMBER,
                               properties=(u'мр',))

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
        self.place.name= self.base_name
        self.place.set_name_forms(self.name_forms)

        self.place.save()
        places_storage.update_version()


    def serialize(self):
        return {'type': self.type_str,
                'base_name': self.base_name,
                'old_name': self.old_name,
                'name_forms': self.name_forms.serialize(),
                'place_id': self.place_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.base_name = data['base_name']
        obj.old_name = data.get('old_name', u'неизвестно')
        obj.name_forms = Noun.deserialize(data['name_forms'])
        obj.place_id = data['place_id']

        return obj
