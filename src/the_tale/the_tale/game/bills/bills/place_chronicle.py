# coding: utf-8

from dext.forms import fields

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, ModeratorFormMixin

from the_tale.game.places import storage as places_storage

from . import base_place_bill


class BaseForm(BaseUserForm):
    place = fields.ChoiceField(label='Город')
    power_bonus = fields.RelationField(label='Изменение влияния', relation=relations.POWER_BONUS_CHANGES)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, ModeratorFormMixin):
    pass


class PlaceChronicle(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_CHRONICLE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Запись в летописи о городе'
    DESCRIPTION = 'В жизни происходит множество интересных событий. Часть из них оказывается достойна занесения в летопись и может немного повлиять на участвующий в них город.'

    def __init__(self, power_bonus=None, **kwargs):
        super(PlaceChronicle, self).__init__(**kwargs)
        self.power_bonus = power_bonus

    def user_form_initials(self):
        data = super(PlaceChronicle, self).user_form_initials()
        data['power_bonus'] = self.power_bonus
        return data

    def initialize_with_form(self, user_form):
        super(PlaceChronicle, self).initialize_with_form(user_form)
        self.power_bonus = user_form.c.power_bonus

    def has_meaning(self):
        return True

    def apply(self, bill=None):
        if not self.has_meaning():
            return

        if self.power_bonus.bonus == 0:
            return

        self.place.cmd_change_power(hero_id=None,
                                    has_place_in_preferences=False,
                                    has_person_in_preferences=False,
                                    power=self.power_bonus.bonus)

    def serialize(self):
        data = super(PlaceChronicle, self).serialize()
        data['power_bonus'] = self.power_bonus.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceChronicle, cls).deserialize(data)
        obj.power_bonus = relations.POWER_BONUS_CHANGES(data['power_bonus'])
        return obj
