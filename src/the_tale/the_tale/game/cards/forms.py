
import smart_imports

smart_imports.all()


class Empty(utils_forms.Form):

    def get_card_data(self):
        return {}


class Person(utils_forms.Form):
    value = utils_fields.ChoiceField(label='Мастер')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = persons_objects.Person.form_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class Place(utils_forms.Form):
    value = utils_fields.ChoiceField(label='Город')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = places_storage.places.get_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class Building(utils_forms.Form):
    value = utils_fields.ChoiceField(label='Строение')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = places_storage.buildings.get_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class CreateClan(utils_forms.Form):
    name = utils_fields.CharField(label='Название',
                                  max_length=clans_models.Clan.MAX_NAME_LENGTH,
                                  min_length=clans_models.Clan.MIN_NAME_LENGTH)
    abbr = utils_fields.CharField(label='Аббревиатура (до %d символов)' % clans_models.Clan.MAX_ABBR_LENGTH,
                                  max_length=clans_models.Clan.MAX_ABBR_LENGTH,
                                  min_length=clans_models.Clan.MIN_ABBR_LENGTH)

    def get_card_data(self):
        return {'name': self.c.name,
                'abbr': self.c.abbr}


class Upbringing(utils_forms.Form):
    value = utils_fields.RelationField(label='происхождение', relation=tt_beings_relations.UPBRINGING)

    def get_card_data(self):
        return {'value': int(self.c.value.value)}


class DeathAge(utils_forms.Form):
    value = utils_fields.RelationField(label='возраст смерти', relation=tt_beings_relations.AGE)

    def get_card_data(self):
        return {'value': int(self.c.value.value)}


class DeathType(utils_forms.Form):
    value = utils_fields.RelationField(label='первая смерть', relation=tt_beings_relations.FIRST_DEATH)

    def get_card_data(self):
        return {'value': int(self.c.value.value)}


class Emissary(utils_forms.Form):
    value = emissaries_fields.EmissaryField()

    def __init__(self, *args, **kwargs):
        clan_id = kwargs.pop('clan_id', None)

        super().__init__(*args, **kwargs)

        self.fields['value'].choices = emissaries_logic.form_choices(own_clan_id=clan_id)

    def get_card_data(self):
        return {'value': int(self.c.value)}
