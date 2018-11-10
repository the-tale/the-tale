
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    place = dext_fields.ChoiceField(label='Город')
    power_bonus = dext_fields.RelationField(label='Изменение влияния', relation=relations.POWER_BONUS_CHANGES)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
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

        impacts = list(places_logic.tt_power_impacts(inner_circle=False,
                                                     actor_type=tt_api_impacts.OBJECT_TYPE.BILL,
                                                     actor_id=bill.id,
                                                     place=self.place,
                                                     amount=self.power_bonus.bonus,
                                                     fame=0))

        politic_power_logic.add_power_impacts(impacts)

    def serialize(self):
        data = super(PlaceChronicle, self).serialize()
        data['power_bonus'] = self.power_bonus.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceChronicle, cls).deserialize(data)
        obj.power_bonus = relations.POWER_BONUS_CHANGES(data['power_bonus'])
        return obj
