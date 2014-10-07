# coding: utf-8

from dext.forms import fields

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.game import names

from the_tale.linguistics.forms import WordField

from the_tale.game.persons.prototypes import PersonPrototype

from the_tale.game.map.places.prototypes import BuildingPrototype

from the_tale.game.bills.relations import BILL_TYPE
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_person_bill import BasePersonBill


class UserForm(BaseUserForm):

    person = fields.ChoiceField(label=u'Житель')

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')

    def __init__(self, choosen_person_id, *args, **kwargs):  # pylint: disable=W0613
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(predicate=lambda place, person: not person.has_building)


class ModeratorForm(BaseModeratorForm):

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')


class BuildingCreate(BasePersonBill):

    type = BILL_TYPE.BUILDING_CREATE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/building_create_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/building_create_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/building_create_show.html'

    CAPTION = u'Возведение постройки'
    # TODO: remove hardcoded url
    DESCRIPTION = u'Возводит здание, принадлежащее выбранному горожанину (и соответствующее его профессии). Один житель города может иметь только одну постройку. Помните, что для поддержания работы здания потребуется участие игроков, иначе оно обветшает и разрушится. О типах зданий можно узнать в <a href="/guide/persons">Путеводителе</a>.'

    def __init__(self, utg_name=None, **kwargs):
        super(BuildingCreate, self).__init__(**kwargs)
        self.building_name_forms = utg_name

    @property
    def base_name(self): return self.building_name_forms.normal_form()

    def apply(self, bill=None):
        if self.person is None or self.person.out_game:
            return

        BuildingPrototype.create(self.person, utg_name=self.building_name_forms)

    @property
    def user_form_initials(self):
        initials = super(BuildingCreate, self).user_form_initials
        initials['name'] = self.building_name_forms
        return initials

    @property
    def moderator_form_initials(self):
        initials = super(BuildingCreate, self).moderator_form_initials
        initials['name'] = self.building_name_forms
        return initials

    def initialize_with_user_data(self, user_form):
        super(BuildingCreate, self).initialize_with_user_data(user_form)
        self.building_name_forms = user_form.c.name

    def initialize_with_moderator_data(self, moderator_form):
        super(BuildingCreate, self).initialize_with_moderator_data(moderator_form)
        self.building_name_forms = moderator_form.c.name

    def serialize(self):
        data = super(BuildingCreate, self).serialize()
        data['building_name_forms'] = self.building_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingCreate, cls).deserialize(data)

        if 'building_name_forms' in data:
            obj.building_name_forms = utg_words.Word.deserialize(data['building_name_forms'])
        else:
            obj.building_name_forms = names.generator.get_fast_name(u'название неизвестно')

        return obj
