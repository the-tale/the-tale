# coding: utf-8

from django.conf import settings as project_settings
from django.forms import ValidationError, Textarea

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.game.bills.models import Bill
from the_tale.game.bills.relations import BILL_DURATION
from the_tale.game.bills.conf import bills_settings


class BaseUserForm(forms.Form):
    RATIONALE_MIN_LENGTH = 250 if not project_settings.TESTS_RUNNING else 0

    caption = fields.CharField(label=u'Название закона', max_length=Bill.CAPTION_MAX_LENGTH, min_length=Bill.CAPTION_MIN_LENGTH)
    rationale = bbcode.BBField(label=u'Обоснование', min_length=RATIONALE_MIN_LENGTH)

    duration = fields.TypedChoiceField(label=u'Время действия', choices=BILL_DURATION.choices(), coerce=BILL_DURATION.get_from_name, required=False)

    chronicle_on_accepted = fields.TextField(label=u'Запись в летопись при принятии', widget=Textarea(attrs={'rows': 2}),
                                             min_length=bills_settings.CHRONICLE_MIN_LENGTH, max_length=bills_settings.CHRONICLE_MAX_LENGTH)
    chronicle_on_ended = fields.TextField(label=u'Запись в летопись при истечении срока действия', widget=Textarea(attrs={'rows': 2}),
                                          min_length=0, max_length=bills_settings.CHRONICLE_MAX_LENGTH, required=False)


    def clean_duration(self):
        data = self.cleaned_data['duration']

        if not data:
            data = BILL_DURATION.UNLIMITED

        return data


    def clean_chronicle_on_ended(self):
        data = self.cleaned_data['chronicle_on_ended']

        if not data:
            return data

        if not (bills_settings.CHRONICLE_MIN_LENGTH <= len(data) <= bills_settings.CHRONICLE_MAX_LENGTH):
            raise ValidationError(u'Длинна записи об истечении действия закона должна быть от %d до %d символов' %
                                  (bills_settings.CHRONICLE_MIN_LENGTH, bills_settings.CHRONICLE_MAX_LENGTH))

        return data

    def clean(self):
        cleaned_data = super(BaseUserForm, self).clean()

        if not cleaned_data['duration'].is_UNLIMITED:
            if not cleaned_data.get('chronicle_on_ended'):
                raise ValidationError(u'Необходимо указать запись в летописи при истечении действия закона')
        else:
            if cleaned_data.get('chronicle_on_ended'):
                raise ValidationError(u'При бесконечном действии закона не надо указывать запись в летопись при истечении его действия')

        return cleaned_data


class BaseModeratorForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрено', required=False)
