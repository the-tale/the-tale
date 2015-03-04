# coding: utf-8

from dext.forms import fields

from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons.storage import persons_storage

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Член Совета')
    power_bonus = fields.RelationField(label=u'Изменение бонуса влияния', relation=relations.POWER_BONUS_CHANGES)

    def __init__(self, choosen_person_id, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(only_weak=False, choosen_person=persons_storage.get(choosen_person_id))


class ModeratorForm(BaseModeratorForm):
    pass


class PersonChronicle(BasePersonBill):
    type = relations.BILL_TYPE.PERSON_CHRONICLE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/person_chronicle_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/person_chronicle_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/person_chronicle_show.html'

    CAPTION = u'Запись в летописи о советнике'
    DESCRIPTION = u'В жизни происходит множество интересных событий. Часть из них оказывается достойна занесения в летопись и может немного повлиять на влиятельность участвующего в них советника.'

    def __init__(self, power_bonus=None, **kwargs):
        super(PersonChronicle, self).__init__(**kwargs)
        self.power_bonus = power_bonus

    def apply(self, bill=None):
        if self.power_bonus.bonus_delta == 0:
            return

        self.person.cmd_change_power(power=0,
                                     positive_bonus=self.power_bonus.bonus_delta if self.power_bonus.bonus_delta > 0 else 0,
                                     negative_bonus=-self.power_bonus.bonus_delta if self.power_bonus.bonus_delta < 0 else 0)


    @property
    def user_form_initials(self):
        initials = super(PersonChronicle, self).user_form_initials
        initials['power_bonus'] = self.power_bonus.value
        return initials

    def initialize_with_user_data(self, user_form):
        super(PersonChronicle, self).initialize_with_user_data(user_form)
        self.power_bonus = user_form.c.power_bonus

    def serialize(self):
        data = super(PersonChronicle, self).serialize()
        data['power_bonus'] = self.power_bonus.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PersonChronicle, cls).deserialize(data)
        obj.power_bonus = relations.POWER_BONUS_CHANGES(data['power_bonus'])
        return obj
