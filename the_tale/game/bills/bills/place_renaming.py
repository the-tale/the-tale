# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.linguistics.forms import WordField

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, ModeratorFormMixin

from the_tale.game.places import storage as places_storage
from the_tale.game.places import logic as places_logic

from . import base_place_bill


class BaseForm(BaseUserForm):
    place = fields.ChoiceField(label=u'Город')
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, ModeratorFormMixin):
    pass


class PlaceRenaming(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = u'Переименование города'
    DESCRIPTION = u'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, name_forms=None, **kwargs):
        super(PlaceRenaming, self).__init__(**kwargs)
        self.name_forms = name_forms

    @property
    def base_name(self): return self.name_forms.normal_form()

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    def user_form_initials(self):
        data = super(PlaceRenaming, self).user_form_initials()
        data['name'] = self.name_forms
        return data

    def initialize_with_user_data(self, user_form):
        super(PlaceRenaming, self).initialize_with_user_data(user_form)
        self.name_forms = user_form.c.name

    def initialize_with_moderator_data(self, moderator_form):
        super(PlaceRenaming, self).initialize_with_moderator_data(moderator_form)
        self.name_forms = moderator_form.c.name

    def has_meaning(self):
        return self.place.utg_name != self.name_forms

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.set_utg_name(self.name_forms)
            places_logic.save_place(self.place)

    def serialize(self):
        data = super(PlaceRenaming, self).serialize()
        data['name_forms'] = self.name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceRenaming, cls).deserialize(data)
        obj.name_forms = utg_words.Word.deserialize(data['name_forms'])
        return obj
