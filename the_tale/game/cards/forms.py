# coding: utf-8

from dext.forms import forms, fields


from the_tale.game.map.places.storage import places_storage


class EmptyForm(forms.Form):
    def get_card_data(self):
        return {}



class PlaceForm(forms.Form):

    place = fields.ChoiceField(label=u'Город')

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()

    def get_card_data(self):
        return {'place_id': int(self.c.place)}
