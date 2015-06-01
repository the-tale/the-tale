# coding: utf-8

from django.conf import settings as project_settings
from django.forms import ValidationError, Textarea

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.game.bills.models import Bill
from the_tale.game.bills.conf import bills_settings


class BaseUserForm(forms.Form):
    RATIONALE_MIN_LENGTH = 250 if not project_settings.TESTS_RUNNING else 0

    caption = fields.CharField(label=u'Название закона', max_length=Bill.CAPTION_MAX_LENGTH, min_length=Bill.CAPTION_MIN_LENGTH)
    rationale = bbcode.BBField(label=u'', min_length=RATIONALE_MIN_LENGTH)

    chronicle_on_accepted = fields.TextField(label=u'Запись в летопись при принятии', widget=Textarea(attrs={'rows': 2}),
                                             min_length=bills_settings.CHRONICLE_MIN_LENGTH, max_length=bills_settings.CHRONICLE_MAX_LENGTH)


class BaseModeratorForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрено', required=False)
