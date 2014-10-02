# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.game import names

from the_tale.linguistics.forms import WORD_FORMS

# from the_tale.game.map.places.models import Place

from the_tale.game.bills.models import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.map.places.storage import places_storage


class UserForm(BaseUserForm, WORD_FORMS[utg_relations.WORD_TYPE.NOUN]):

    place = fields.ChoiceField(label=u'Город')

    # TODO: restrict max place name
    # new_name = fields.CharField(label=u'Новое название', max_length=Place.MAX_NAME_LENGTH)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()

    @property
    def name_drawer(self):
        from the_tale.linguistics import word_drawer
        return word_drawer.FormDrawer(self.WORD_TYPE, form=self)



class ModeratorForm(BaseModeratorForm, WORD_FORMS[utg_relations.WORD_TYPE.NOUN]):
    pass

    @property
    def name_drawer(self):
        from the_tale.linguistics import word_drawer
        return word_drawer.FormDrawer(self.WORD_TYPE, form=self)



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
        initials = WORD_FORMS[utg_relations.WORD_TYPE.NOUN].get_initials(self.name_forms)
        initials.update({'place': self.place_id})
        return initials

    @property
    def moderator_form_initials(self):
        initials = WORD_FORMS[utg_relations.WORD_TYPE.NOUN].get_initials(self.name_forms)
        return initials

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.old_name_forms = self.place.utg_name
        self.name_forms = user_form.get_word()

    def initialize_with_moderator_data(self, moderator_form):
        self.name_forms = moderator_form.get_word()

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
