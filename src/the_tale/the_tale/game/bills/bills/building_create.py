
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    person = dext_fields.ChoiceField(label='Житель')
    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN,
                                       label='Название',
                                       skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))
    x = django_forms.IntegerField(label='координата x')
    y = django_forms.IntegerField(label='координата y')

    def __init__(self, choosen_person_id, *args, **kwargs):  # pylint: disable=W0613
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = persons_objects.Person.form_choices(predicate=lambda place, person: not person.has_building)

    def clean(self):
        person_id = int(self.cleaned_data['person'])
        x = int(self.cleaned_data['x'])
        y = int(self.cleaned_data['y'])

        person = persons_storage.persons[person_id]

        if (x, y) not in places_logic.get_available_positions(center_x=person.place.x, center_y=person.place.y):
            raise django_forms.ValidationError('Здание не может быть возведено на выбранных координатах')

        return self.cleaned_data


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class BuildingCreate(base_person_bill.BasePersonBill):
    type = relations.BILL_TYPE.BUILDING_CREATE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Возведение постройки'
    # TODO: remove hardcoded url
    DESCRIPTION = 'Возводит здание, принадлежащее выбранному Мастеру (и соответствующее его профессии). Один Мастер может иметь только одну постройку. Помните, что для поддержания работы здания потребуется участие игроков, иначе оно обветшает и перестанет давать бонусы. О типах зданий можно узнать в <a href="/guide/persons">Путеводителе</a>. '

    def __init__(self, utg_name=None, x=None, y=None, **kwargs):
        super(BuildingCreate, self).__init__(**kwargs)
        self.building_name_forms = utg_name
        self.x = x
        self.y = y

    @property
    def base_name(self):
        return self.building_name_forms.normal_form()

    def has_meaning(self):
        return (self.person and
                places_storage.buildings.get_by_person_id(self.person.id) is None and
                (self.x, self.y) in places_logic.get_available_positions(center_x=self.person.place.x, center_y=self.person.place.y))

    def apply(self, bill=None):
        if self.has_meaning():
            places_logic.create_building(self.person,
                                         utg_name=self.building_name_forms,
                                         position=(self.x, self.y))

    def user_form_initials(self):
        initials = super(BuildingCreate, self).user_form_initials()
        initials['name'] = self.building_name_forms
        initials['x'] = self.x
        initials['y'] = self.y
        return initials

    def initialize_with_form(self, user_form):
        super(BuildingCreate, self).initialize_with_form(user_form)
        self.building_name_forms = user_form.c.name
        self.x = user_form.c.x
        self.y = user_form.c.y

    def serialize(self):
        data = super(BuildingCreate, self).serialize()
        data['building_name_forms'] = self.building_name_forms.serialize()
        data['x'] = self.x
        data['y'] = self.y
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(BuildingCreate, cls).deserialize(data)

        if 'building_name_forms' in data:
            obj.building_name_forms = utg_words.Word.deserialize(data['building_name_forms'])
        else:
            obj.building_name_forms = game_names.generator().get_fast_name('название утрачено')

        obj.x = data.get('x')
        obj.y = data.get('y')

        return obj
