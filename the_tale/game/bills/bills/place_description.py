# coding: utf-8
import postmarkup

from dext.forms import fields

from textgen.words import Noun

from common.utils.forms import BBField

from game.bills.models import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm

from game.map.places.storage import places_storage
from game.map.places.conf import places_settings

class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    new_description = BBField(label=u'Новое описание', max_length=places_settings.MAX_DESCRIPTION_LENGTH)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = [(place.id, place.name) for place in sorted(places_storage.all(), key=lambda p: p.name)]


class ModeratorForm(BaseModeratorForm):
    pass


class PlaceDescripton(object):

    type = BILL_TYPE.PLACE_DESCRIPTION
    type_str = BILL_TYPE._ID_TO_STR[BILL_TYPE.PLACE_DESCRIPTION].lower()

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_description_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_description_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_description_show.html'

    CAPTION = u'Закон об изменении описания города'
    DESCRIPTION = u'Изменяет описание города. При создании нового описания постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается. Также не забывайте, что описание должно соответствовать названию города. Описание должно быть небольшим по размеру.'

    def __init__(self, place_id=None, description=None, old_name_forms=None, old_description=None):
        self.place_id = place_id
        self.description = description
        self.old_name_forms = old_name_forms
        self.old_description = old_description

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.normalized_name

    @property
    def description_html(self): return postmarkup.render_bbcode(self.description)

    @property
    def old_description_html(self): return postmarkup.render_bbcode(self.old_description)

    @property
    def old_name(self): return self.old_name_forms.normalized

    @property
    def place(self):
        return places_storage[self.place_id]

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'new_description': self.description}

    @property
    def moderator_form_initials(self):
        return {}

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.description = user_form.c.new_description
        self.old_name_forms = self.place.normalized_name
        self.old_description = self.place.description

    def initialize_with_moderator_data(self, moderator_form):
        pass

    @classmethod
    def get_user_form_create(cls, post=None):
        return cls.UserForm(post)

    def get_user_form_update(self, post=None, initial=None):
        if initial:
            return self.UserForm(initial=initial)
        return  self.UserForm(post)

    def apply(self):
        self.place.description= self.description
        self.place.save()
        places_storage.update_version()


    def serialize(self):
        return {'type': self.type_str,
                'description': self.description,
                'place_id': self.place_id,
                'old_name_forms': self.old_name_forms.serialize(),
                'old_description': self.old_description}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.description = data['description']
        obj.place_id = data['place_id']

        if 'old_name_forms' in data:
            obj.old_name_forms = Noun.deserialize(data['old_name_forms'])
        else:
            obj.old_name_forms = Noun.fast_construct(u'название неизвестно')

        obj.old_description = data.get('old_description', u'неизвестно')

        return obj
