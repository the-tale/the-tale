# coding: utf-8

from dext.forms import forms, fields


from the_tale.game.map.places.storage import places_storage, buildings_storage
from the_tale.game.persons.prototypes import PersonPrototype


class EmptyForm(forms.Form):
    def get_card_data(self):
        return {}


class PersonForm(forms.Form):

    person = fields.ChoiceField(label=u'Советник')

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['person'].choices = PersonPrototype.form_choices(only_weak=False)

    def get_card_data(self):
        return {'person_id': int(self.c.person)}


class PlaceForm(forms.Form):

    place = fields.ChoiceField(label=u'Город')

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()

    def get_card_data(self):
        return {'place_id': int(self.c.place)}


class BuildingForm(forms.Form):

    building = fields.ChoiceField(label=u'Строение')

    def __init__(self, *args, **kwargs):
        super(BuildingForm, self).__init__(*args, **kwargs)
        self.fields['building'].choices = buildings_storage.get_choices()

    def get_card_data(self):
        return {'building_id': int(self.c.building)}
