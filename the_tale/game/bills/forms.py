# coding: utf-8

from dext.forms import forms, fields

from common.utils import bbcode

from game.bills.models import Bill


class BaseUserForm(forms.Form):

    caption = fields.CharField(label=u'Название закона', max_length=Bill.CAPTION_MAX_LENGTH, min_length=Bill.CAPTION_MIN_LENGTH)
    rationale = bbcode.BBField(label=u'Обоснование')

class BaseModeratorForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрено', required=False)
