# coding: utf-8

from dext.forms import forms, fields


from the_tale.game.map.places.storage import places_storage


class PlaceForm(forms.Form):

    place = fields.ChoiceField(label=u'Город')

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()
