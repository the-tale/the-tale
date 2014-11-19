# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.game import names

from the_tale.linguistics.forms import WordField

from the_tale.game.bills.models import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.map.places.storage import places_storage


class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))
    # TODO: restrict max place name
    # new_name = fields.CharField(label=u'Новое название', max_length=Place.MAX_NAME_LENGTH)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()

class ModeratorForm(BaseModeratorForm):
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')


class PlaceRenaming(BaseBill):

    type = BILL_TYPE.PLACE_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_renaming_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_renaming_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_renaming_show.html'

    CAPTION = u'Переименование города'
    DESCRIPTION = u'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, place_id=None, name_forms=None, old_name_forms=None):
        super(PlaceRenaming, self).__init__()
        self.place_id = place_id
        self.name_forms = name_forms
        self.old_name_forms = old_name_forms

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.utg_name

    @property
    def place(self): return places_storage[self.place_id]

    @property
    def actors(self): return [self.place]

    @property
    def base_name(self): return self.name_forms.normal_form()

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'name': self.name_forms}

    @property
    def moderator_form_initials(self):
        return {'name': self.name_forms}

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.old_name_forms = self.place.utg_name
        self.name_forms = user_form.c.name

    def initialize_with_moderator_data(self, moderator_form):
        self.name_forms = moderator_form.c.name

    def apply(self, bill=None):
        self.place.set_utg_name(self.name_forms)
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
            obj.old_name_forms = utg_words.Word.deserialize(data['old_name_forms'])
        else:
            obj.old_name_forms = names.generator.get_fast_name(u'название неизвестно')

        obj.name_forms = utg_words.Word.deserialize(data['name_forms'])
        obj.place_id = data['place_id']

        return obj
