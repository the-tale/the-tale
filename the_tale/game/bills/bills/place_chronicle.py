# coding: utf-8

from dext.forms import fields

from utg import words as utg_words

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.map.places.storage import places_storage


class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    power_bonus = fields.RelationField(label=u'Изменение бонуса влияния', relation=relations.POWER_BONUS_CHANGES)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()


class ModeratorForm(BaseModeratorForm):
    pass


class PlaceChronicle(BaseBill):

    type = relations.BILL_TYPE.PLACE_CHRONICLE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_chronicle_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_chronicle_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_chronicle_show.html'

    CAPTION = u'Запись в летописи о городе'
    DESCRIPTION = u'В жизни происходит множество интересных событий. Часть из них оказывается достойна занесения в летопись и может немного повлиять на участвующий в них город.'

    def __init__(self, place_id=None, old_name_forms=None, power_bonus=None):
        super(PlaceChronicle, self).__init__()
        self.place_id = place_id
        self.old_name_forms = old_name_forms
        self.power_bonus = power_bonus

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.utg_name

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place(self): return places_storage[self.place_id]

    @property
    def actors(self): return [self.place]

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'power_bonus': self.power_bonus.value}

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.power_bonus = user_form.c.power_bonus
        self.old_name_forms = self.place.utg_name

    def apply(self, bill=None):
        if self.power_bonus.bonus_delta == 0:
            return

        self.place.cmd_change_power(power=0,
                                     positive_bonus=self.power_bonus.bonus_delta if self.power_bonus.bonus_delta > 0 else 0,
                                     negative_bonus=-self.power_bonus.bonus_delta if self.power_bonus.bonus_delta < 0 else 0)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'place_id': self.place_id,
                'old_name_forms': self.old_name_forms.serialize(),
                'power_bonus': self.power_bonus.value}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.place_id = data['place_id']
        obj.power_bonus = relations.POWER_BONUS_CHANGES(data['power_bonus'])
        obj.old_name_forms = utg_words.Word.deserialize(data['old_name_forms'])

        return obj
