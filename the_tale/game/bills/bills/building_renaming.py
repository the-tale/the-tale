# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.linguistics.forms import WORD_FORMS

from the_tale.game.persons.prototypes import PersonPrototype

from the_tale.game.map.places.storage import buildings_storage

from the_tale.game.bills.relations import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm, WORD_FORMS[utg_relations.WORD_TYPE.NOUN]):

    person = fields.ChoiceField(label=u'Житель')

    def __init__(self, choosen_person_id, *args, **kwargs): # pylint: disable=W0613
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(predicate=self._person_has_building)

    @classmethod
    def _person_has_building(cls, place, person): # pylint: disable=W0613
        return buildings_storage.get_by_person_id(person.id) is not None

    @property
    def name_drawer(self):
        from the_tale.linguistics import word_drawer
        return word_drawer.FormDrawer(self.WORD_TYPE, form=self)



class ModeratorForm(BaseModeratorForm, WORD_FORMS[utg_relations.WORD_TYPE.NOUN]):

    @property
    def name_drawer(self):
        from the_tale.linguistics import word_drawer
        return word_drawer.FormDrawer(self.WORD_TYPE, form=self)



class BuildingRenaming(BasePersonBill):

    type = BILL_TYPE.BUILDING_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_renaming_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_renaming_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_renaming_show.html'

    CAPTION = u'Переименование постройки'
    DESCRIPTION = u'Изменяет название постройки, принадлежащей выбранному горожанину.'

    def __init__(self, old_building_name_forms=None, new_building_name_forms=None, **kwargs):
        super(BuildingRenaming, self).__init__(**kwargs)

        self.old_building_name_forms = old_building_name_forms
        self.new_building_name_forms = new_building_name_forms

        if self.old_building_name_forms is None:
            building = buildings_storage.get_by_person_id(self.person_id)
            if building is not None:
                self.old_building_name_forms = building.utg_name

    @property
    def old_name(self): return self.old_building_name_forms.normal_form()

    @property
    def new_name(self): return self.new_building_name_forms.normal_form()

    def apply(self, bill=None):
        building = buildings_storage.get_by_person_id(self.person.id)

        if building is None or building.state.is_DESTROYED:
            return

        building.set_utg_name(self.new_building_name_forms)
        building.save()


    @property
    def user_form_initials(self):
        initials = super(BuildingRenaming, self).user_form_initials
        initials.update(WORD_FORMS[utg_relations.WORD_TYPE.NOUN].get_initials(self.new_building_name_forms))
        return initials

    @property
    def moderator_form_initials(self):
        initials = super(BuildingRenaming, self).moderator_form_initials
        initials.update(WORD_FORMS[utg_relations.WORD_TYPE.NOUN].get_initials(self.new_building_name_forms))
        return initials

    def initialize_with_user_data(self, user_form):
        super(BuildingRenaming, self).initialize_with_user_data(user_form)
        self.new_building_name_forms = user_form.get_word()

        building = buildings_storage.get_by_person_id(self.person_id)
        if building is not None:
            self.old_building_name_forms = building.utg_name

    def initialize_with_moderator_data(self, moderator_form):
        super(BuildingRenaming, self).initialize_with_moderator_data(moderator_form)
        self.new_building_name_forms = moderator_form.get_word()

    def serialize(self):
        data = super(BuildingRenaming, self).serialize()
        data['old_building_name_forms'] = self.old_building_name_forms.serialize()
        data['new_building_name_forms'] = self.new_building_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingRenaming, cls).deserialize(data)
        obj.old_building_name_forms = utg_words.Word.deserialize(data['old_building_name_forms'])
        obj.new_building_name_forms = utg_words.Word.deserialize(data['new_building_name_forms'])

        return obj
