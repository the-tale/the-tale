# coding: utf-8

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.game.bills.models import Bill
from the_tale.game.bills.relations import BILL_DURATION


class BaseUserForm(forms.Form):
    RATIONALE_MIN_LENGTH = 250

    caption = fields.CharField(label=u'Название закона', max_length=Bill.CAPTION_MAX_LENGTH, min_length=Bill.CAPTION_MIN_LENGTH)
    rationale = bbcode.BBField(label=u'Обоснование', min_length=RATIONALE_MIN_LENGTH)
    duration = fields.TypedChoiceField(label=u'Время действия', choices=BILL_DURATION.choices(), coerce=BILL_DURATION.get_from_name, required=False)

    def clean_duration(self):
        data = self.cleaned_data['duration']

        if not data:
            data = BILL_DURATION.UNLIMITED

        return data


class BaseModeratorForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрено', required=False)
