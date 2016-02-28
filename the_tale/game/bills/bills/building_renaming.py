# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.linguistics.forms import WordField

from the_tale.game.persons import objects as persons_objects

from the_tale.game.places import storage as places_storage

from the_tale.game.bills.relations import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Житель')
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))

    def __init__(self, choosen_person_id, *args, **kwargs): # pylint: disable=W0613
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = persons_objects.Person.form_choices(predicate=self._person_has_building)

    @classmethod
    def _person_has_building(cls, place, person): # pylint: disable=W0613
        return places_storage.buildings.get_by_person_id(person.id) is not None


class ModeratorForm(BaseModeratorForm):
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')


class BuildingRenaming(BasePersonBill):

    type = BILL_TYPE.BUILDING_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = u'Переименование постройки'
    DESCRIPTION = u'Изменяет название постройки, принадлежащей выбранному горожанину.'

    def __init__(self, old_building_name_forms=None, new_building_name_forms=None, **kwargs):
        super(BuildingRenaming, self).__init__(**kwargs)

        self.old_building_name_forms = old_building_name_forms
        self.new_building_name_forms = new_building_name_forms

        if self.old_building_name_forms is None:
            building = places_storage.buildings.get_by_person_id(self.person_id)
            if building is not None:
                self.old_building_name_forms = building.utg_name

    @property
    def old_name(self): return self.old_building_name_forms.normal_form()

    @property
    def new_name(self): return self.new_building_name_forms.normal_form()

    @property
    def building(self): return places_storage.buildings.get_by_person_id(self.person.id)

    def has_meaning(self):
        return self.building and not self.building.state.is_DESTROYED and self.building.utg_name != self.new_building_name_forms

    def apply(self, bill=None):
        if self.has_meaning():
            self.building.set_utg_name(self.new_building_name_forms)
            self.building.save()


    @property
    def user_form_initials(self):
        initials = super(BuildingRenaming, self).user_form_initials
        initials['name'] = self.new_building_name_forms
        return initials

    @property
    def moderator_form_initials(self):
        initials = super(BuildingRenaming, self).moderator_form_initials
        initials['name'] = self.new_building_name_forms
        return initials

    def initialize_with_user_data(self, user_form):
        super(BuildingRenaming, self).initialize_with_user_data(user_form)
        self.new_building_name_forms = user_form.c.name

        building = places_storage.buildings.get_by_person_id(self.person_id)
        if building is not None:
            self.old_building_name_forms = building.utg_name

    def initialize_with_moderator_data(self, moderator_form):
        super(BuildingRenaming, self).initialize_with_moderator_data(moderator_form)
        self.new_building_name_forms = moderator_form.c.name

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
