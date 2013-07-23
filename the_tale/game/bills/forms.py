# coding: utf-8

from dext.forms import forms, fields

from common.utils import bbcode

from game.bills.models import Bill
from game.bills.relations import BILL_DURATION


class BaseUserForm(forms.Form):

    caption = fields.CharField(label=u'Название закона', max_length=Bill.CAPTION_MAX_LENGTH, min_length=Bill.CAPTION_MIN_LENGTH)
    rationale = bbcode.BBField(label=u'Обоснование')
    duration = fields.TypedChoiceField(label=u'Время действия', choices=BILL_DURATION._choices(), coerce=BILL_DURATION._get_from_name, required=False)

    def clean_duration(self):
        data = self.cleaned_data['duration']

        if not data:
            data = BILL_DURATION.UNLIMITED

        return data


class BaseModeratorForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрено', required=False)
