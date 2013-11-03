# coding: utf-8

from dext.forms import fields

from textgen.words import Noun

from the_tale.common.utils.forms import SimpleWordField

from the_tale.game.map.places.models import Place

from the_tale.game.bills.models import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.map.places.storage import places_storage

class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    new_name = fields.CharField(label=u'Новое название', max_length=Place.MAX_NAME_LENGTH)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()


class ModeratorForm(BaseModeratorForm):

    name_forms = SimpleWordField(label=u'Формы названия')


class PlaceRenaming(BaseBill):

    type = BILL_TYPE.PLACE_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_renaming_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_renaming_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_renaming_show.html'

    CAPTION = u'Переименование города'
    DESCRIPTION = u'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, place_id=None, base_name=None, name_forms=None, old_name_forms=None):
        super(PlaceRenaming, self).__init__()
        self.place_id = place_id
        self.name_forms = name_forms
        self.old_name_forms = old_name_forms

        if self.name_forms is None and base_name is not None:
            self.name_forms = Noun.fast_construct(base_name)

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.normalized_name

    @property
    def place(self): return places_storage[self.place_id]

    @property
    def actors(self): return [self.place]

    @property
    def base_name(self): return self.name_forms.normalized

    @property
    def old_name(self): return self.old_name_forms.normalized

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

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

    def apply(self, bill=None):
        self.place.set_name_forms(self.name_forms)
        self.place.save()

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
