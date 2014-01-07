# coding: utf-8

from dext.forms import fields

from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons.storage import persons_storage

from the_tale.game.bills.relations import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Член Совета')

    def __init__(self, choosen_person_id, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(only_weak=True, choosen_person=persons_storage.get(choosen_person_id))


class ModeratorForm(BaseModeratorForm):
    pass


class PersonRemove(BasePersonBill):

    type = BILL_TYPE.PERSON_REMOVE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/person_remove_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/person_remove_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/person_remove_show.html'

    CAPTION = u'Исключение из Совета'
    DESCRIPTION = u'В случае, если горожанин утратил доверие духов-хранителей, его можно исключить из Совета города. Исключать можно только наименее влиятельных советников (но советник будет исключён, даже если за время голосования существенно увеличит своё влияние и станет самым влиятельным горожанином).'

    def apply(self, bill=None):
        self.person.move_out_game()
        self.person.place.sync_persons(force_add=False)
        self.person.place.save()
        self.person.save()
